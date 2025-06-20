from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
from src.graph.traveller import compile_with_checkpointer
from src.models import Flight

app = FastAPI()

DEBUG = True


@app.get("/healthz")
def health_check():
    from datetime import datetime, timezone

    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


class TripPlanningRequest(BaseModel):
    trip_details: str


@app.post("/trip/planning")
async def trip_planning(request: TripPlanningRequest):
    traveller_graph = compile_with_checkpointer()

    config = {
        "configurable": {"thread_id": "traveller-123"},
    }

    def event_stream():
        for step in traveller_graph.stream(
            {"trip_details": request.trip_details}, config=config, stream_mode="updates"
        ):
            current_node = list(step.keys())[0]
            current_node_values = list(step.values())[0]

            if DEBUG:
                print("node values", current_node_values)

            if current_node == "flights_search_node":
                data = {
                    "response": f"Found {len(current_node_values['flights'])} flights options. I will rank them and return the best options for you"
                }
            elif current_node == "flights_ranking_node":
                ranked_flights: list[Flight] = current_node_values.get("ranked_flights", [])

                data = {
                    "response": current_node_values["friendly_greeting"],
                    "flights": [flight.model_dump(mode="json") for flight in ranked_flights],
                }
            else:
                data = {"response": "Working on your request..."}

            yield (
                JSONResponse(
                    content=data,
                    media_type="application/json",
                ).body.decode()
                + "\n"
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
