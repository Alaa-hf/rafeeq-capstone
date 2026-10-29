
import json
import agentkit as K

executed = []

# Simulated booking tool - does not modify any database
def book_inspection(permit_id: str) -> dict:
    executed.append(permit_id)
    return {"status": "booked"}

class TestShape:
    def __init__(self):
        self.round = 0

    def start(self, system, task, history=None):
        return [{"role": "user", "content": task}]

    def step(self, state, tools, model, **kwargs):
        self.round += 1

        if self.round == 1:
            return K.Turn(
                text="",
                calls=[
                    K.Call(
                        id="test-call-1",
                        name="book_inspection",
                        arguments=json.dumps({"permit_id": "TEST-001"})
                    )
                ]
            )

        return K.Turn(text="Booking was not executed.", calls=[])

    def add_results(self, state, results):
        for call, output in results:
            state.append({"role": "tool", "content": output})


def permission(name, args):
    return "ask" if name == "book_inspection" else "allow"


run = K.run_agent(
    "Book an inspection",
    [book_inspection],
    shape=TestShape(),
    permission=permission,
    approve=lambda name, args: False,
    max_steps=3,
    verbose=True
)

assert executed == [], "FAIL: Booking was executed!"
assert any(e.kind == "guard" and "denied" in e.text for e in run.trace)

print("\nPASS: Booking blocked by HITL.")
print("Final:", run.final)