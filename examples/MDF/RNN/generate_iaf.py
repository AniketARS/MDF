"""
    Example of ModECI MDF - Testing integrate and fire neurons
"""

from modeci_mdf.mdf import *
import sys


def main():
    mod = Model(id="IAFs")
    mod_graph = Graph(id="iaf_example")
    mod.graphs.append(mod_graph)

    ## Counter node
    input_node = Node(id="input_node")

    t_param = Parameter(id="t", default_initial_value=0, time_derivative="1")
    input_node.parameters.append(t_param)

    start = Parameter(id="start", value=20)
    input_node.parameters.append(start)

    dur = Parameter(id="duration", value=60)
    input_node.parameters.append(dur)

    amp = Parameter(id="amplitude", value=10)
    input_node.parameters.append(amp)

    level = Parameter(id="level", value=0)

    level.conditions.append(
        ParameterCondition(
            id="on", test="t > start and t < start + duration", value=amp.id
        )
    )
    level.conditions.append(
        ParameterCondition(id="off", test="t > start + duration", value=0)
    )

    input_node.parameters.append(level)

    op1 = OutputPort(id="out_port", value=level.id)
    input_node.output_ports.append(op1)

    op2 = OutputPort(id="t_out_port", value=t_param.id)
    input_node.output_ports.append(op2)

    mod_graph.nodes.append(input_node)

    ## IAF node...
    iaf_node = Node(id="iaf_node")
    ip1 = InputPort(id="input")
    iaf_node.input_ports.append(ip1)

    erev = Parameter(id="erev", value=-70)
    iaf_node.parameters.append(erev)
    tau = Parameter(id="tau", value=10)
    iaf_node.parameters.append(tau)
    thresh = Parameter(id="thresh", value=-20)
    iaf_node.parameters.append(thresh)

    # v_init = Parameter(id="v_init", value=-30)
    # iaf_node.parameters.append(v_init)

    pc = ParameterCondition(id="reset", test="v > thresh", value="erev")

    v = Parameter(
        id="v",
        default_initial_value="-50",
        time_derivative="-1 * (v-erev)/tau + input",
    )
    v.conditions.append(pc)

    iaf_node.parameters.append(v)

    op1 = OutputPort(id="out_port", value="v")
    iaf_node.output_ports.append(op1)
    mod_graph.nodes.append(iaf_node)

    e1 = Edge(
        id="input_edge",
        parameters={"weight": 1},
        sender=input_node.id,
        sender_port=op1.id,
        receiver=iaf_node.id,
        receiver_port=ip1.id,
    )

    mod_graph.edges.append(e1)

    new_file = mod.to_json_file("%s.json" % mod.id)
    new_file = mod.to_yaml_file("%s.yaml" % mod.id)

    if "-run" in sys.argv:

        verbose = "-v" in sys.argv

        from modeci_mdf.utils import load_mdf, print_summary

        from modeci_mdf.execution_engine import EvaluableGraph

        eg = EvaluableGraph(mod_graph, verbose)
        dt = 0.1

        duration = 100
        t_ext = 0
        recorded = {}
        times = []
        t = []
        i = []
        s = []
        while t_ext <= duration:
            times.append(t_ext)
            print("======   Evaluating at t = %s  ======" % (t_ext))
            if t_ext == 0:
                eg.evaluate()  # replace with initialize?
            else:
                eg.evaluate(time_increment=dt)

            i.append(eg.enodes["input_node"].evaluable_outputs["out_port"].curr_value)
            t.append(eg.enodes["input_node"].evaluable_outputs["t_out_port"].curr_value)
            s.append(eg.enodes["iaf_node"].evaluable_outputs["out_port"].curr_value)
            t_ext += dt

        import matplotlib.pyplot as plt

        plt.plot(times, t, label="time at input node")
        plt.plot(times, i, label="state of input node")
        plt.plot(times, s, label="IaF 0 state")
        plt.legend()

        plt.savefig("IaF.run.png", bbox_inches="tight")

        if "-nogui" not in sys.argv:
            plt.show()

    if "-graph" in sys.argv:
        mod.to_graph_image(
            engine="dot",
            output_format="png",
            view_on_render=False,
            level=3,
            filename_root="iaf",
            only_warn_on_fail=True,  # Makes sure test of this doesn't fail on Windows on GitHub Actions
        )

    return mod_graph


if __name__ == "__main__":
    main()
