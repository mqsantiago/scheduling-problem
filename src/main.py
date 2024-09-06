import sam


def main():
    sa_solution, sa_modes, sa_cost = sam.sa_procedure()

    print(f"Best Solution so far: \n{sa_solution} \n{sa_modes}")
    print(f"Project Length: {sa_cost}")

    resource_met = sam.nonrenewable_resources_constraints_met(sa_solution, sa_modes)
    print(f"Non-renewable resources constrains met: {resource_met}")


main()
