import asyncio
import solara


@solara.component
def Page():
    var = solara.use_reactive(0)
    progress, set_progress = solara.use_state(False)
    click, set_click = solara.use_state(0)

    def run_async():
        async def some_task(param=3) -> int:
            await asyncio.sleep(param / 2)
            return param * 2

        async def main():
            aws = list(some_task(i) for i in range(10))
            result = []
            for i, coro in enumerate(asyncio.as_completed(aws)):
                result.append(await coro)
                set_progress(lambda progress: progress + 10)

            set_progress(False)
            var.value = sum(result)

        set_progress(True)
        asyncio.create_task(main())

    solara.Button("RUN", on_click=run_async)
    solara.Text(str(var.value))
    solara.ProgressLinear(progress)

    solara.Button(f"Clicked: {int(click)}", on_click=lambda: set_click(click + 1))
