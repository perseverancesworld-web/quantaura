from .enochian import EnochianInterpreter, Context, Aethyr, Watchtower, parse_program


def run_example():
    """Test in different Watchtowers to demo semantics."""
    for wt_name in ["EAST", "WEST", "NORTH", "SOUTH"]:
        print(f"\n=== Running in {wt_name} Watchtower ===")
        interpreter = EnochianInterpreter()

        program_source = """
CALL_2 {
  PA TABLE_ALPHA
  UR TABLE_ALPHA
  TAL PATTERN_DENSITY
  IF TAL > 0.5 {
    EL AETHYR_25
    LUX RELATIONS
    MED ARCHETYPESET CURRENTPATTERN
  }
  MOS
}
"""

        program = parse_program(program_source)

        initial_ctx = Context(
            watchtower=Watchtower[wt_name],
            aethyr=Aethyr(18)
        )

        interpreter.run(program, initial_ctx)

        print("Events:")
        for event in interpreter.events:
            print(f"  {event.opcode}@{event.aethyr}: {event.target} {event.payload}")

        print("  TAL value:", interpreter.variables.get("TAL", "N/A"))


if __name__ == "__main__":
    run_example()
