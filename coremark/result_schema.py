import pydantic
class CoremarkResults(pydantic.BaseModel):
        iteration: int = pydantic.Field(description="Iteration", gt=0)
        threads: int = pydantic.Field(description="How many threads we ran.", gt=0)
        test_passes: float = pydantic.Field(description="Number of test passes", allow_inf_nan=False, gt=0, validation_alias="test passes")
