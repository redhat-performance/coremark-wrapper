import pydantic
import datetime

class CoremarkResults(pydantic.BaseModel):
    iteration: int = pydantic.Field(gt=0)
    threads: int = pydantic.Field(gt=0)
    IterationsPerSec: float = pydantic.Field(gt=0, allow_inf_nan=False)
    Start_Date: datetime.datetime
    End_Date: datetime.datetime
