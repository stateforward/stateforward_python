import stateforward as sf


def create_sm(regions: int):
    class SM(sf.AsyncStateMachine):
        for x in range(regions):
            exec(
                f"""class r{x}(sf.Region):
    class s1(sf.State):
        pass
    initial = sf.initial(s1)
            """
            )

    print("here", SM.r0.initial)
    return SM


sf.dump(create_sm(1))
