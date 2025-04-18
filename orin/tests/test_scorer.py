"""Tests for the intent scoring pipeline."""
import pytest
from orin.scoring.intent_scorer import IntentScorer, ProspectSignals, SCORING_THRESHOLD


class TestIntentScorer:
    """Test suite for prospect scoring."""

    def test_scoring_threshold_default(self):
        """Default threshold should be 0.7."""
        assert SCORING_THRESHOLD == 0.7

    def test_prospect_signals_creation(self):
        """ProspectSignals should accept minimal data."""
        signals = ProspectSignals(company_name="TestCo")
        assert signals.company_name == "TestCo"
        assert signals.website_url is None

    def test_prospect_signals_full(self):
        """ProspectSignals should accept full data."""
        signals = ProspectSignals(
            company_name="BigStore",
            website_url="https://bigstore.com",
            industry="e-commerce",
            employee_count=50,
            tech_stack=["shopify", "klaviyo"],
            recent_funding=2_000_000,
            social_activity_score=7.5,
            website_traffic_rank=45000,
        )
        assert signals.employee_count == 50
        assert len(signals.tech_stack) == 2
