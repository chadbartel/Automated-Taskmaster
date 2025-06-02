# Standard Library
from typing import List

# Third Party
import pytest
from pydantic import ValidationError

# First Party
from automated_taskmaster.models.monster import (
    Monster,
    MonsterSummonRequest,
    MonsterSummonResponse,
)


class TestMonsterSummonRequest:
    """Test cases for MonsterSummonRequest model."""

    def test_create_with_defaults(self) -> None:
        """Test creating MonsterSummonRequest with default values."""
        # Arrange & Act
        request = MonsterSummonRequest()

        # Assert
        assert request.cr_min is None
        assert request.cr_max is None
        assert request.environment is None
        assert request.limit == 10

    def test_create_with_all_fields(self) -> None:
        """Test creating MonsterSummonRequest with all fields provided."""
        # Arrange
        cr_min = 1.0
        cr_max = 5.0
        environment = "forest"
        limit = 25

        # Act
        request = MonsterSummonRequest(
            cr_min=cr_min,
            cr_max=cr_max,
            environment=environment,
            limit=limit
        )

        # Assert
        assert request.cr_min == cr_min
        assert request.cr_max == cr_max
        assert request.environment == environment
        assert request.limit == limit

    @pytest.mark.parametrize("cr_min", [0, 0.0, 0.5, 1.0, 10.5])
    def test_cr_min_valid_values(self, cr_min: float) -> None:
        """Test MonsterSummonRequest with valid cr_min values."""
        # Arrange & Act
        request = MonsterSummonRequest(cr_min=cr_min)

        # Assert
        assert request.cr_min == cr_min

    @pytest.mark.parametrize("cr_max", [0, 0.0, 0.5, 1.0, 10.5])
    def test_cr_max_valid_values(self, cr_max: float) -> None:
        """Test MonsterSummonRequest with valid cr_max values."""
        # Arrange & Act
        request = MonsterSummonRequest(cr_max=cr_max)

        # Assert
        assert request.cr_max == cr_max

    @pytest.mark.parametrize("limit", [1, 25, 50])
    def test_limit_valid_values(self, limit: int) -> None:
        """Test MonsterSummonRequest with valid limit values."""
        # Arrange & Act
        request = MonsterSummonRequest(limit=limit)

        # Assert
        assert request.limit == limit

    @pytest.mark.parametrize("cr_min", [-1, -0.1, -10])
    def test_cr_min_invalid_negative_values(self, cr_min: float) -> None:
        """Test MonsterSummonRequest validation fails for negative cr_min."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            MonsterSummonRequest(cr_min=cr_min)

        assert "greater than or equal to 0" in str(exc_info.value)

    @pytest.mark.parametrize("cr_max", [-1, -0.1, -10])
    def test_cr_max_invalid_negative_values(self, cr_max: float) -> None:
        """Test MonsterSummonRequest validation fails for negative cr_max."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            MonsterSummonRequest(cr_max=cr_max)

        assert "greater than or equal to 0" in str(exc_info.value)

    @pytest.mark.parametrize("limit", [0, -1, 51, 100])
    def test_limit_invalid_values(self, limit: int) -> None:
        """Test MonsterSummonRequest validation fails for invalid limit."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            MonsterSummonRequest(limit=limit)

        error_message = str(exc_info.value)
        assert "greater than or equal to 1" in error_message or \
               "less than or equal to 50" in error_message


class TestMonster:
    """Test cases for Monster model."""

    def test_create_monster_with_float_cr(self) -> None:
        """Test creating Monster with float challenge rating."""
        # Arrange
        name = "Goblin"
        cr = 0.25
        environment = ["forest", "hills"]
        source = "Monster Manual"

        # Act
        monster = Monster(
            name=name,
            cr=cr,
            environment=environment,
            source=source
        )

        # Assert
        assert monster.name == name
        assert monster.cr == cr
        assert monster.environment == environment
        assert monster.source == source

    def test_create_monster_with_string_cr(self) -> None:
        """Test creating Monster with string challenge rating."""
        # Arrange
        name = "Ancient Dragon"
        cr = "30"
        environment = ["mountain", "cave"]
        source = "Monster Manual"

        # Act
        monster = Monster(
            name=name,
            cr=cr,
            environment=environment,
            source=source
        )

        # Assert
        assert monster.name == name
        assert monster.cr == cr
        assert monster.environment == environment
        assert monster.source == source

    def test_create_monster_with_single_environment(self) -> None:
        """Test creating Monster with single environment in list."""
        # Arrange
        name = "Fire Elemental"
        cr = 5.0
        environment = ["desert"]
        source = "Monster Manual"

        # Act
        monster = Monster(
            name=name,
            cr=cr,
            environment=environment,
            source=source
        )

        # Assert
        assert monster.name == name
        assert monster.cr == cr
        assert monster.environment == environment
        assert monster.source == source

    def test_create_monster_with_multiple_environments(self) -> None:
        """Test creating Monster with multiple environments."""
        # Arrange
        name = "Owlbear"
        cr = 3.0
        environment = ["forest", "grassland", "hill"]
        source = "Monster Manual"

        # Act
        monster = Monster(
            name=name,
            cr=cr,
            environment=environment,
            source=source
        )

        # Assert
        assert monster.name == name
        assert monster.cr == cr
        assert monster.environment == environment
        assert monster.source == source

    def test_monster_missing_required_fields(self) -> None:
        """Test Monster validation fails when required fields are missing."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Monster()

        error_message = str(exc_info.value)
        assert "name" in error_message
        assert "cr" in error_message
        assert "environment" in error_message
        assert "source" in error_message

    @pytest.mark.parametrize("missing_field,field_value", [
        ("name", {"cr": 1.0, "environment": ["forest"], "source": "MM"}),
        ("cr", {"name": "Goblin", "environment": ["forest"], "source": "MM"}),
        ("environment", {"name": "Goblin", "cr": 1.0, "source": "MM"}),
        ("source", {"name": "Goblin", "cr": 1.0, "environment": ["forest"]}),
    ])
    def test_monster_missing_individual_required_fields(
        self, missing_field: str, field_value: dict
    ) -> None:
        """Test Monster validation fails for each missing required field."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Monster(**field_value)

        assert missing_field in str(exc_info.value)


class TestMonsterSummonResponse:
    """Test cases for MonsterSummonResponse model."""

    def test_create_response_with_empty_monsters(self) -> None:
        """Test creating MonsterSummonResponse with empty monster list."""
        # Arrange
        query_parameters = MonsterSummonRequest()
        summoned_monsters: List[Monster] = []
        count = 0

        # Act
        response = MonsterSummonResponse(
            query_parameters=query_parameters,
            summoned_monsters=summoned_monsters,
            count=count
        )

        # Assert
        assert response.query_parameters == query_parameters
        assert response.summoned_monsters == summoned_monsters
        assert response.count == count

    def test_create_response_with_single_monster(self) -> None:
        """Test creating MonsterSummonResponse with single monster."""
        # Arrange
        query_parameters = MonsterSummonRequest(
            cr_min=1.0,
            cr_max=3.0,
            environment="forest"
        )
        monster = Monster(
            name="Goblin",
            cr=0.25,
            environment=["forest", "hills"],
            source="Monster Manual"
        )
        summoned_monsters = [monster]
        count = 1

        # Act
        response = MonsterSummonResponse(
            query_parameters=query_parameters,
            summoned_monsters=summoned_monsters,
            count=count
        )

        # Assert
        assert response.query_parameters == query_parameters
        assert response.summoned_monsters == summoned_monsters
        assert response.count == count
        assert len(response.summoned_monsters) == 1
        assert response.summoned_monsters[0] == monster

    def test_create_response_with_multiple_monsters(self) -> None:
        """Test creating MonsterSummonResponse with multiple monsters."""
        # Arrange
        query_parameters = MonsterSummonRequest(limit=2)
        monsters = [
            Monster(
                name="Goblin",
                cr=0.25,
                environment=["forest"],
                source="Monster Manual"
            ),
            Monster(
                name="Orc",
                cr=1.0,
                environment=["mountains"],
                source="Monster Manual"
            )
        ]
        count = 2

        # Act
        response = MonsterSummonResponse(
            query_parameters=query_parameters,
            summoned_monsters=monsters,
            count=count
        )

        # Assert
        assert response.query_parameters == query_parameters
        assert response.summoned_monsters == monsters
        assert response.count == count
        assert len(response.summoned_monsters) == 2

    def test_response_missing_required_fields(self) -> None:
        """Test MonsterSummonResponse validation fails for missing fields."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            MonsterSummonResponse()

        error_message = str(exc_info.value)
        assert "query_parameters" in error_message
        assert "summoned_monsters" in error_message
        assert "count" in error_message

    @pytest.mark.parametrize("missing_field,field_value", [
        ("query_parameters", {
            "summoned_monsters": [],
            "count": 0
        }),
        ("summoned_monsters", {
            "query_parameters": MonsterSummonRequest(),
            "count": 0
        }),
        ("count", {
            "query_parameters": MonsterSummonRequest(),
            "summoned_monsters": []
        }),
    ])
    def test_response_missing_individual_required_fields(
        self, missing_field: str, field_value: dict
    ) -> None:
        """Test MonsterSummonResponse validation for each missing field."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            MonsterSummonResponse(**field_value)

        assert missing_field in str(exc_info.value)


class TestModelIntegration:
    """Integration tests for all models working together."""

    def test_complete_workflow(self) -> None:
        """Test complete workflow from request to response."""
        # Arrange
        request = MonsterSummonRequest(
            cr_min=0.0,
            cr_max=2.0,
            environment="forest",
            limit=3
        )

        monsters = [
            Monster(
                name="Goblin",
                cr=0.25,
                environment=["forest", "hills"],
                source="Monster Manual"
            ),
            Monster(
                name="Wolf",
                cr="0.25",
                environment=["forest", "grassland"],
                source="Monster Manual"
            ),
            Monster(
                name="Brown Bear",
                cr=1.0,
                environment=["forest"],
                source="Monster Manual"
            )
        ]

        # Act
        response = MonsterSummonResponse(
            query_parameters=request,
            summoned_monsters=monsters,
            count=len(monsters)
        )

        # Assert
        assert response.query_parameters.cr_min == 0.0
        assert response.query_parameters.cr_max == 2.0
        assert response.query_parameters.environment == "forest"
        assert response.query_parameters.limit == 3
        assert len(response.summoned_monsters) == 3
        assert response.count == 3

        # Verify each monster
        goblin = response.summoned_monsters[0]
        assert goblin.name == "Goblin"
        assert goblin.cr == 0.25
        assert "forest" in goblin.environment

        wolf = response.summoned_monsters[1]
        assert wolf.name == "Wolf"
        assert wolf.cr == "0.25"  # String CR

        bear = response.summoned_monsters[2]
        assert bear.name == "Brown Bear"
        assert bear.cr == 1.0

    def test_model_serialization_deserialization(self) -> None:
        """Test that models can be serialized and deserialized properly."""
        # Arrange
        original_request = MonsterSummonRequest(
            cr_min=1.5,
            cr_max=5.0,
            environment="cave"
        )

        # Act - Convert to dict and back
        request_dict = original_request.model_dump()
        reconstructed_request = MonsterSummonRequest(**request_dict)        # Assert
        assert reconstructed_request.cr_min == original_request.cr_min
        assert reconstructed_request.cr_max == original_request.cr_max
        assert reconstructed_request.environment == original_request.environment
        assert reconstructed_request.limit == original_request.limit