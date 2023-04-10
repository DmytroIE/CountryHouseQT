import pydux

from src.features.Watering.Reducers.WateringZonesReducer import watering_zones_reducer
from src.features.Watering.Reducers.WateringCyclesReducer import watering_cycles_reducer
from src.features.Watering.Reducers.WateringDurationsReducer import watering_durations_reducer
from src.features.Watering.Reducers.WateringProcessReducer import watering_process_reducer

watering_reducer = pydux.combine_reducers({'zones': watering_zones_reducer,
                                           'cycles': watering_cycles_reducer,
                                           'durations': watering_durations_reducer,
                                           'process': watering_process_reducer
                                           })
