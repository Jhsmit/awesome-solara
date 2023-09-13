import solara
import asyncio

from dask.distributed import Client

from awesome_solara.multiprocess.my_task import some_task

# make sure a cluster is running here
adresss = "tcp://127.0.0.1:62138"


# problem: futures cancel immediately
@solara.component
def Page():
    var = solara.use_reactive(0)
    click, set_click = solara.use_state(0)
    progress, set_progress = solara.use_state(0)

    def run_async():
        async def main():
            async with Client(adresss, asynchronous=True) as client:
                futures = []
                for i in range(10):
                    future = client.submit(some_task, i)
                    futures.append(future)

                print("tasks", futures)
                # results = await asyncio.gather(*futures)

                results = []
                for i, coro in enumerate(asyncio.as_completed(futures)):
                    result = await coro
                    results.append(result)
                    set_progress(lambda progress: progress + 10)

                var.value = sum(results)

        set_progress(True)
        asyncio.create_task(main())
        print("false?")

    solara.Button("RUN", on_click=run_async)
    solara.Text(str(var.value))
    solara.ProgressLinear(progress)

    solara.Button(f"Clicked: {int(click)}", on_click=lambda: set_click(click + 1))
