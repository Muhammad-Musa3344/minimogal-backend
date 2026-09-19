# app/schemas/screen_5.py
"""
Pydantic contracts and data transfer objects for Screen 5: Flavor & Quantity Selection.
Prepared for MOGUL-12 / MOGUL-13 / MOGUL-14 implementation.

This module defines:
- Option retrieval models (flavors, quantities, nudge rules)
- Decision submission & validation request/response models
- Persisted JSONB shape in decision_log table
- Mock data provider fallback (used if DS 3x tables are delayed)
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class FlavorOption(BaseModel):
    """Represents an individual flavor selection choice."""
    id: str = Field(..., description="Unique code for the flavor, e.g. 'flavor_cherry'")
    name: str = Field(..., description="Display title for the flavor, e.g. 'Cherry Blast'")
    description: Optional[str] = Field(None, description="Short child-friendly description")
    color_hex: str = Field(..., description="Hex code for stand/lollipop rendering, e.g. '#E63946'")
    icon_url: Optional[str] = Field(None, description="URL or asset path for flavor icon")
    is_unlocked: bool = Field(True, description="Whether this flavor is accessible at the player's level")
    is_premium: bool = Field(False, description="Whether this flavor has premium ingredient costs")


class QuantityOption(BaseModel):
    """Represents an allowable batch quantity option."""
    units: int = Field(..., gt=0, description="Total number of lollipops to produce, e.g. 20, 50, 100")
    label: str = Field(..., description="Display label, e.g. '20 Lollipops'")
    tag: Optional[str] = Field(None, description="Helpful tag, e.g. 'Starter Batch', 'Standard Batch'")
    is_recommended: bool = Field(False, description="Default recommended option for beginners")


class NudgeRule(BaseModel):
    """AI Nudge rule definition surfaced to frontend for live interaction hints."""
    rule_id: str = Field(..., description="Identifier for the heuristic rule")
    trigger_type: str = Field(..., description="Condition type: 'high_quantity', 'low_flavor_variety', etc.")
    trigger_quantity_min: Optional[int] = Field(None, description="Minimum batch quantity triggering this nudge")
    trigger_quantity_max: Optional[int] = Field(None, description="Maximum batch quantity triggering this nudge")
    trigger_flavor_count_max: Optional[int] = Field(None, description="Maximum flavor count triggering this nudge")
    copy_text: str = Field(..., description="Child-friendly hint text displayed in speech bubble")
    audio_url: Optional[str] = Field(None, description="Optional audio narration URL")


class Screen5OptionsResponse(BaseModel):
    """Response payload for GET /api/v1/screens/screen-5/options."""
    kid_session_id: UUID = Field(..., description="Active player session ID")
    level: int = Field(1, ge=1, le=3, description="Gameplay level derived from age (1: 7-8, 2: 9-10, 3: 11-14)")
    wallet_balance_cents: int = Field(..., ge=0, description="Current live wallet balance in cents (read-only)")
    max_flavors_allowed: int = Field(2, ge=1, le=5, description="Max distinct flavors the player may choose")
    flavor_options: List[FlavorOption] = Field(..., description="Catalog of available flavors for this level")
    quantity_options: List[QuantityOption] = Field(..., description="Allowable batch sizes for this level")
    nudge_rules: List[NudgeRule] = Field(default_factory=list, description="Contextual nudge trigger rules")
    data_source: str = Field("mock_fallback", description="'ds_confirmed' or 'mock_fallback'")


class Screen5DecisionRequest(BaseModel):
    """Request payload for POST /api/v1/screens/screen-5/decisions."""
    kid_session_id: UUID = Field(..., description="Active player session ID")
    selected_flavors: List[str] = Field(..., min_length=1, description="List of chosen flavor IDs")
    batch_quantity: int = Field(..., gt=0, description="Chosen batch size (must match allowed options)")
    nudge_fired_id: Optional[str] = Field(None, description="ID of any AI nudge displayed to the kid")

    @field_validator("selected_flavors")
    @classmethod
    def validate_flavor_uniqueness(cls, v: List[str]) -> List[str]:
        if len(v) != len(set(v)):
            raise ValueError("Duplicate flavors cannot be selected in a single batch")
        return v


class Screen5PersistedPayload(BaseModel):
    """Structured payload stored inside decision_log.decision_value (JSONB)."""
    selected_flavors: List[str] = Field(..., description="List of chosen flavor IDs")
    flavor_count: int = Field(..., ge=1, description="Count of distinct flavors chosen")
    batch_quantity: int = Field(..., gt=0, description="Chosen batch size")
    nudge_fired_id: Optional[str] = Field(None, description="Fired nudge ID for analytics")


class Screen5DecisionResponse(BaseModel):
    """Response payload for POST /api/v1/screens/screen-5/decisions."""
    status: str = Field("success", description="Outcome status")
    decision_id: UUID = Field(..., description="Generated decision_log row ID")
    kid_session_id: UUID = Field(..., description="Player session ID")
    screen_id: str = Field("screen_5", description="Screen identifier")
    persisted_payload: Screen5PersistedPayload = Field(..., description="Persisted decision data")
    next_screen: str = Field("screen_6", description="Next screen in flow (Screen 6: Prep Level)")


class Screen5DecisionStateResponse(BaseModel):
    """Response payload for GET /api/v1/screens/screen-5/decisions/{kid_session_id}."""
    has_decision: bool = Field(..., description="Whether a decision has been recorded for this screen")
    decision_id: Optional[UUID] = Field(None, description="decision_log row ID if found")
    persisted_payload: Optional[Screen5PersistedPayload] = Field(None, description="Saved decision details")
    created_at: Optional[str] = Field(None, description="ISO timestamp of when decision was logged")


class MockFlavorQuantityProvider:
    """
    Fallback data provider for Screen 5.
    Guarantees deterministic, level-aware options matching PRD specifications
    if Data Science's tables are delayed.
    """

    @staticmethod
    def get_options_for_level(level: int) -> dict:
        level_flavors = {
            1: [
                FlavorOption(
                    id="flavor_cherry",
                    name="Cherry Blast",
                    description="Sweet and juicy all-time classic",
                    color_hex="#E63946",
                    icon_url="https://assets.minimogul.app/flavors/cherry.svg",
                    is_unlocked=True,
                    is_premium=False,
                ),
                FlavorOption(
                    id="flavor_blue_raspberry",
                    name="Blue Raspberry",
                    description="Tangy and refreshing crowd favorite",
                    color_hex="#457B9D",
                    icon_url="https://assets.minimogul.app/flavors/blue_raspberry.svg",
                    is_unlocked=True,
                    is_premium=False,
                ),
                FlavorOption(
                    id="flavor_lemon",
                    name="Lemon Zing",
                    description="Bright, sunny, and sour citrus flavor",
                    color_hex="#F4A261",
                    icon_url="https://assets.minimogul.app/flavors/lemon.svg",
                    is_unlocked=True,
                    is_premium=False,
                ),
            ],
            2: [
                FlavorOption(
                    id="flavor_cherry",
                    name="Cherry Blast",
                    description="Sweet and juicy all-time classic",
                    color_hex="#E63946",
                    icon_url="https://assets.minimogul.app/flavors/cherry.svg",
                    is_unlocked=True,
                    is_premium=False,
                ),
                FlavorOption(
                    id="flavor_blue_raspberry",
                    name="Blue Raspberry",
                    description="Tangy and refreshing crowd favorite",
                    color_hex="#457B9D",
                    icon_url="https://assets.minimogul.app/flavors/blue_raspberry.svg",
                    is_unlocked=True,
                    is_premium=False,
                ),
                FlavorOption(
                    id="flavor_lemon",
                    name="Lemon Zing",
                    description="Bright, sunny, and sour citrus flavor",
                    color_hex="#F4A261",
                    icon_url="https://assets.minimogul.app/flavors/lemon.svg",
                    is_unlocked=True,
                    is_premium=False,
                ),
                FlavorOption(
                    id="flavor_watermelon",
                    name="Watermelon Wave",
                    description="Summer sensation with real watermelon notes",
                    color_hex="#2A9D8F",
                    icon_url="https://assets.minimogul.app/flavors/watermelon.svg",
                    is_unlocked=True,
                    is_premium=True,
                ),
            ],
            3: [
                FlavorOption(
                    id="flavor_cherry",
                    name="Cherry Blast",
                    description="Sweet and juicy all-time classic",
                    color_hex="#E63946",
                    icon_url="https://assets.minimogul.app/flavors/cherry.svg",
                    is_unlocked=True,
                    is_premium=False,
                ),
                FlavorOption(
                    id="flavor_blue_raspberry",
                    name="Blue Raspberry",
                    description="Tangy and refreshing crowd favorite",
                    color_hex="#457B9D",
                    icon_url="https://assets.minimogul.app/flavors/blue_raspberry.svg",
                    is_unlocked=True,
                    is_premium=False,
                ),
                FlavorOption(
                    id="flavor_lemon",
                    name="Lemon Zing",
                    description="Bright, sunny, and sour citrus flavor",
                    color_hex="#F4A261",
                    icon_url="https://assets.minimogul.app/flavors/lemon.svg",
                    is_unlocked=True,
                    is_premium=False,
                ),
                FlavorOption(
                    id="flavor_watermelon",
                    name="Watermelon Wave",
                    description="Summer sensation with real watermelon notes",
                    color_hex="#2A9D8F",
                    icon_url="https://assets.minimogul.app/flavors/watermelon.svg",
                    is_unlocked=True,
                    is_premium=True,
                ),
                FlavorOption(
                    id="flavor_mango_tango",
                    name="Mango Tango",
                    description="Exotic tropical blend for adventurous moguls",
                    color_hex="#E76F51",
                    icon_url="https://assets.minimogul.app/flavors/mango.svg",
                    is_unlocked=True,
                    is_premium=True,
                ),
            ],
        }

        level_quantities = {
            1: [
                QuantityOption(units=20, label="20 Lollipops", tag="Starter Batch", is_recommended=True),
                QuantityOption(units=40, label="40 Lollipops", tag="Standard Batch", is_recommended=False),
                QuantityOption(units=60, label="60 Lollipops", tag="Mega Batch", is_recommended=False),
            ],
            2: [
                QuantityOption(units=25, label="25 Lollipops", tag="Starter Batch", is_recommended=True),
                QuantityOption(units=50, label="50 Lollipops", tag="Standard Batch", is_recommended=False),
                QuantityOption(units=100, label="100 Lollipops", tag="Mega Batch", is_recommended=False),
            ],
            3: [
                QuantityOption(units=30, label="30 Lollipops", tag="Starter Batch", is_recommended=False),
                QuantityOption(units=60, label="60 Lollipops", tag="Standard Batch", is_recommended=True),
                QuantityOption(units=120, label="120 Lollipops", tag="Mega Batch", is_recommended=False),
            ],
        }

        level_nudges = {
            1: [
                NudgeRule(
                    rule_id="nudge_l1_high_qty",
                    trigger_type="high_quantity",
                    trigger_quantity_min=60,
                    copy_text="Whoa, 60 lollipops is a huge batch! Make sure you save enough money to make them in the next step.",
                ),
                NudgeRule(
                    rule_id="nudge_l1_single_flavor",
                    trigger_type="low_flavor_variety",
                    trigger_flavor_count_max=1,
                    copy_text="Offering 2 flavors gives your customers more choices to love!",
                ),
            ],
            2: [
                NudgeRule(
                    rule_id="nudge_l2_high_qty",
                    trigger_type="high_quantity",
                    trigger_quantity_min=100,
                    copy_text="100 lollipops requires significant upfront cash for ingredients. Keep an eye on your wallet balance!",
                ),
            ],
            3: [
                NudgeRule(
                    rule_id="nudge_l3_high_qty",
                    trigger_type="high_quantity",
                    trigger_quantity_min=120,
                    copy_text="High inventory increases potential profit, but unsold lollipops will cut into your bottom line!",
                ),
            ],
        }

        max_flavors_map = {1: 2, 2: 3, 3: 4}

        return {
            "flavors": level_flavors.get(level, level_flavors[1]),
            "quantities": level_quantities.get(level, level_quantities[1]),
            "nudges": level_nudges.get(level, level_nudges[1]),
            "max_flavors": max_flavors_map.get(level, 2),
        }
