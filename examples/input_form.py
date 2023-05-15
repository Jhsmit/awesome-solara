import contextlib
from functools import partial
from typing import Callable, Union, Optional, Annotated

import solara
from solara import Reactive
from solara.alias import rv
from pydantic import ValidationError, BaseModel, Field


@solara.component
def ValidationForm(value: Union[BaseModel, Reactive[BaseModel]], on_value: Optional[Callable[[BaseModel], None]] = None, layout=None, field_options=None, global_options=None):
    field_options = field_options or {}
    global_options = global_options or {}

    # value of the pydantic model
    model_value = solara.use_reactive(value, on_value)

    # value of the form, allows for illegal values
    form_value = solara.use_reactive(model_value.value.dict())

    # dictionary with error messages from validation
    error_value = solara.use_reactive({k: [] for k in model_value.value.__fields__})

    def updater(name, value):
        form_value.update(**{name: value})
        try:
            model_value.update(**{name: value})
            if error_value.value[name]:
                error_value.update(**{name: []})
        except ValidationError as e:
            errors = e.errors()
            if len(errors) > 1:
                raise ValueError("Can only handle one error") from e
            error = errors[0]
            error_value.update(**{name: [error['msg']]})

    layout_cm = layout or solara.Column
    with layout_cm():
        for name, field in model_value.value.__fields__.items():
            upd_func = partial(updater, name)
            f_opt = field_options.get(name, {})

            if tooltip := field.field_info.description:
                cm = solara.Tooltip(tooltip)
            else:
                cm = contextlib.nullcontext()

            label = field.field_info.title or humanize_snake_case(name)
            textfield_kwargs = dict(label=label, v_model=form_value.value[name], error_messages=error_value.value[name], on_v_model=upd_func, **f_opt, **global_options)

            with cm:
                rv.TextField(**textfield_kwargs)

    solara.Button(label='print', on_click=lambda: print(model_value.value))


def humanize_snake_case(s: str) -> str:
    # the human already thought about humanization or does not stick to snake_case
    if any(c.isupper() for c in s):
        return s
    else:
        return s.replace('_', ' ').title()


class ExperimentMetadata(BaseModel):

    experiment_label: Annotated[str, Field(description="Label for the experiment.", max_length=10)] = "Experiment 1"

    pH: Annotated[float, Field(le=14, ge=2., description="Uncorrected pH as read with a pH meter")] = 7.0

    temperature: Annotated[float, Field(ge=0., le=100,  title="Temperature (C)", description="Temperature reaction mixture.")] = 25.0


@solara.component
def Page():
    global_exp_metadata = solara.use_reactive(ExperimentMetadata())

    field_options = {'temperature': {'suffix': '\u2103'}}
    ValidationForm(global_exp_metadata, field_options=field_options)