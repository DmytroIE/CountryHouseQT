import pydux

from src.features.Watering.Reducers.WateringReducer import watering_reducer

root_reducer = pydux.combine_reducers({'watering': watering_reducer
                                       })

store = pydux.create_store(root_reducer)
