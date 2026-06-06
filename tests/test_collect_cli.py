from chomsky.collect.cli import build_arg_parser


def test_parser_exposes_all_subcommands():
    p = build_arg_parser()
    for cmd in ["export", "ingest", "aggregate", "confirm", "perception"]:
        args = p.parse_args([cmd])
        assert args.command == cmd


def test_aggregate_has_threshold_default():
    args = build_arg_parser().parse_args(["aggregate"])
    assert args.threshold == 0.66


def test_perception_requires_axis_with_default():
    args = build_arg_parser().parse_args(["perception"])
    assert args.axis == "region"
