from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np
import solara
import asyncio
import time


def some_task(param=3) -> int:
    time.sleep(param / 2)
    return param * 2


executor_class = ProcessPoolExecutor  # or ThreadPoolExecutor


@solara.component
def Page():
    var = solara.use_reactive(0)
    click, set_click = solara.use_state(0)
    progress, set_progress = solara.use_state(0)

    def run_async():
        async def main():
            loop = asyncio.get_running_loop()
            tasks = []
            with executor_class(max_workers=2) as pool:
                for i in range(10):
                    task = loop.run_in_executor(pool, some_task, i)
                    tasks.append(task)

                results = []
                for i, coro in enumerate(asyncio.as_completed(tasks)):
                    result = await coro
                    results.append(result)
                    set_progress(i * 10)
                    print("progress", progress)  # this is always 0

                set_progress(False)
                var.value = sum(results)

        set_progress(True)
        asyncio.create_task(main())

    solara.Button("RUN", on_click=run_async)
    solara.Text(str(var.value))
    solara.ProgressLinear(progress)

    solara.Button(f"Clicked: {int(click)}", on_click=lambda: set_click(click + 1))
