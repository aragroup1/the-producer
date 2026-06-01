"""Automation Rules Engine.

IF/THEN rule system for autonomous marketing decisions.
Supports conditions on metrics, trends, and performance data.
"""

import os
import json
import operator
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

logger = structlog.get_logger()


class ComparisonOp(Enum):
    """Comparison operators."""
    EQ = "=="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class LogicalOp(Enum):
    """Logical operators for combining conditions."""
    AND = "and"
    OR = "or"


@dataclass
class Condition:
    """A single condition."""
    metric: str  # e.g., "ctr", "views", "genre"
    operator: str  # ComparisonOp value
    value: Any
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition against context."""
        actual_value = context.get(self.metric)
        
        if actual_value is None:
            return False
        
        op_map = {
            "==": operator.eq,
            "!=": operator.ne,
            ">": operator.gt,
            ">=": operator.ge,
            "<": operator.lt,
            "<=": operator.le,
            "contains": lambda a, b: str(b).lower() in str(a).lower(),
            "starts_with": lambda a, b: str(a).lower().startswith(str(b).lower()),
            "ends_with": lambda a, b: str(a).lower().endswith(str(b).lower()),
            "in": lambda a, b: a in b if isinstance(b, (list, tuple, set)) else str(a) in str(b),
        }
        
        op_func = op_map.get(self.operator)
        if not op_func:
            logger.warning("unknown_operator", operator=self.operator)
            return False
        
        try:
            return op_func(actual_value, self.value)
        except Exception as e:
            logger.warning("condition_eval_failed", 
                         metric=self.metric, error=str(e))
            return False


@dataclass
class Rule:
    """An automation rule."""
    id: str
    name: str
    description: str
    conditions: List[Condition]
    logical_op: str  # "and" or "or"
    actions: List[Dict[str, Any]]
    enabled: bool = True
    trigger_count: int = 0
    last_triggered: Optional[str] = None
    cooldown_hours: int = 24
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate all conditions."""
        if not self.conditions:
            return False
        
        results = [c.evaluate(context) for c in self.conditions]
        
        if self.logical_op == "and":
            return all(results)
        else:  # "or"
            return any(results)
    
    def can_trigger(self) -> bool:
        """Check if rule can trigger (cooldown)."""
        if not self.last_triggered:
            return True
        
        try:
            last = datetime.fromisoformat(self.last_triggered)
            cooldown = timedelta(hours=self.cooldown_hours)
            return datetime.now() - last >= cooldown
        except (ValueError, TypeError):
            return True
    
    def record_trigger(self):
        """Record that rule was triggered."""
        self.trigger_count += 1
        self.last_triggered = datetime.now().isoformat()


class RuleEngine:
    """Automation rules engine."""
    
    # Pre-built rules
    DEFAULT_RULES = [
        Rule(
            id="high_ctr_drill",
            name="High CTR Drill Boost",
            description="If drill beats have high CTR, increase drill uploads",
            conditions=[
                Condition(metric="genre", operator="==", value="drill"),
                Condition(metric="ctr", operator=">", value=0.05)
            ],
            logical_op="and",
            actions=[
                {"type": "increase_uploads", "genre": "drill", "amount": 2},
                {"type": "log", "message": "Drill CTR high - increasing uploads"}
            ],
            cooldown_hours=12
        ),
        Rule(
            id="trending_emotional_guitar",
            name="Emotional Guitar Trend Spike",
            description="If emotional guitar trends spike, generate more content",
            conditions=[
                Condition(metric="trend_keyword", operator="contains", value="emotional guitar"),
                Condition(metric="trend_growth", operator=">", value=2.0)
            ],
            logical_op="and",
            actions=[
                {"type": "generate_batch", "genre": "emotional", "count": 10},
                {"type": "notify", "message": "Emotional guitar trend detected!"}
            ],
            cooldown_hours=6
        ),
        Rule(
            id="low_ctr_thumbnail",
            name="Low CTR Thumbnail Alert",
            description="If CTR is low, flag for thumbnail A/B test",
            conditions=[
                Condition(metric="ctr", operator="<", value=0.02),
                Condition(metric="impressions", operator=">", value=1000)
            ],
            logical_op="and",
            actions=[
                {"type": "create_ab_test", "test_type": "thumbnail"},
                {"type": "log", "message": "Low CTR detected - creating thumbnail A/B test"}
            ],
            cooldown_hours=48
        ),
        Rule(
            id="viral_opportunity",
            name="Viral Opportunity Capture",
            description="If a video starts trending, boost promotion",
            conditions=[
                Condition(metric="views_per_hour", operator=">", value=1000),
                Condition(metric="subscriber_conversion", operator=">", value=0.05)
            ],
            logical_op="and",
            actions=[
                {"type": "boost_promotion", "boost_factor": 2.0},
                {"type": "create_shorts", "from_video": "auto"},
                {"type": "notify", "message": "Viral opportunity detected!"}
            ],
            cooldown_hours=4
        ),
        Rule(
            id="weekend_upload_boost",
            name="Weekend Upload Boost",
            description="Increase upload frequency on weekends",
            conditions=[
                Condition(metric="day_of_week", operator="in", value=[5, 6])  # Saturday, Sunday
            ],
            logical_op="and",
            actions=[
                {"type": "increase_uploads", "factor": 1.5},
                {"type": "log", "message": "Weekend boost activated"}
            ],
            cooldown_hours=24
        ),
        Rule(
            id="thumbnail_ab_winner",
            name="Thumbnail A/B Winner Apply",
            description="If A/B test has clear winner, apply to future uploads",
            conditions=[
                Condition(metric="ab_test_confidence", operator=">", value=0.95),
                Condition(metric="ab_test_ctr_improvement", operator=">", value=0.2)
            ],
            logical_op="and",
            actions=[
                {"type": "set_default_thumbnail", "variant": "winner"},
                {"type": "log", "message": "A/B test winner applied as default"}
            ],
            cooldown_hours=72
        ),
    ]
    
    def __init__(self, storage_path: str = "./output/rules.json"):
        self.storage_path = storage_path
        self.rules: Dict[str, Rule] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self.load()
        
        # Register default rules
        if not self.rules:
            for rule in self.DEFAULT_RULES:
                self.rules[rule.id] = rule
            self.save()
    
    def load(self):
        """Load rules from storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for rule_data in data:
                        conditions = [
                            Condition(**c) for c in rule_data.get('conditions', [])
                        ]
                        rule = Rule(
                            id=rule_data['id'],
                            name=rule_data['name'],
                            description=rule_data.get('description', ''),
                            conditions=conditions,
                            logical_op=rule_data.get('logical_op', 'and'),
                            actions=rule_data.get('actions', []),
                            enabled=rule_data.get('enabled', True),
                            trigger_count=rule_data.get('trigger_count', 0),
                            last_triggered=rule_data.get('last_triggered'),
                            cooldown_hours=rule_data.get('cooldown_hours', 24),
                            created_at=rule_data.get('created_at')
                        )
                        self.rules[rule.id] = rule
            except Exception as e:
                logger.warning("rules_load_failed", error=str(e))
    
    def save(self):
        """Save rules to storage."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = []
        for rule in self.rules.values():
            rule_dict = asdict(rule)
            rule_dict['conditions'] = [asdict(c) for c in rule.conditions]
            data.append(rule_dict)
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def register_action_handler(self, action_type: str, 
                                 handler: Callable[[Dict[str, Any]], Any]):
        """Register a handler for an action type."""
        self.action_handlers[action_type] = handler
    
    def evaluate_all(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate all rules and return triggered actions.
        
        Args:
            context: Dict with metrics like ctr, views, genre, etc.
        
        Returns:
            List of triggered actions
        """
        triggered = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            if not rule.can_trigger():
                continue
            
            try:
                if rule.evaluate(context):
                    rule.record_trigger()
                    
                    logger.info("rule_triggered",
                               rule_id=rule.id,
                               rule_name=rule.name)
                    
                    # Execute actions
                    for action in rule.actions:
                        result = self._execute_action(action)
                        triggered.append({
                            'rule_id': rule.id,
                            'rule_name': rule.name,
                            'action': action,
                            'result': result
                        })
            
            except Exception as e:
                logger.error("rule_eval_error", 
                           rule_id=rule.id, error=str(e))
        
        if triggered:
            self.save()
        
        return triggered
    
    def _execute_action(self, action: Dict[str, Any]) -> Any:
        """Execute a single action."""
        action_type = action.get('type', 'unknown')
        
        handler = self.action_handlers.get(action_type)
        if handler:
            try:
                return handler(action)
            except Exception as e:
                logger.error("action_handler_failed", 
                           action_type=action_type, error=str(e))
                return None
        else:
            # Default logging for unhandled actions
            logger.info("action_executed", action=action)
            return {'status': 'logged', 'action': action}
    
    def add_rule(self, rule: Rule):
        """Add a new rule."""
        self.rules[rule.id] = rule
        self.save()
        logger.info("rule_added", rule_id=rule.id, name=rule.name)
    
    def remove_rule(self, rule_id: str):
        """Remove a rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.save()
            logger.info("rule_removed", rule_id=rule_id)
    
    def enable_rule(self, rule_id: str):
        """Enable a rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            self.save()
    
    def disable_rule(self, rule_id: str):
        """Disable a rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            self.save()
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID."""
        return self.rules.get(rule_id)
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """List all rules with status."""
        return [
            {
                'id': r.id,
                'name': r.name,
                'description': r.description,
                'enabled': r.enabled,
                'trigger_count': r.trigger_count,
                'last_triggered': r.last_triggered,
                'conditions_count': len(r.conditions),
                'actions_count': len(r.actions)
            }
            for r in self.rules.values()
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rule engine statistics."""
        total = len(self.rules)
        enabled = sum(1 for r in self.rules.values() if r.enabled)
        total_triggers = sum(r.trigger_count for r in self.rules.values())
        
        recently_triggered = [
            r for r in self.rules.values()
            if r.last_triggered and 
            datetime.now() - datetime.fromisoformat(r.last_triggered) < timedelta(days=7)
        ]
        
        return {
            'total_rules': total,
            'enabled_rules': enabled,
            'disabled_rules': total - enabled,
            'total_triggers': total_triggers,
            'recently_triggered': len(recently_triggered),
            'top_rules': sorted(
                [{'name': r.name, 'triggers': r.trigger_count} for r in self.rules.values()],
                key=lambda x: x['triggers'],
                reverse=True
            )[:5]
        }
