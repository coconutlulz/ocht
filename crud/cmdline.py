import argparse
from ast import literal_eval

from crud.controllers import controller_mapping
from crud.views import view_mapping


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "operation",
        choices=["get", "create", "update", "filter", "deactivate"]
    )
    parser.add_argument(
        "type",
        choices=["sport", "event", "selection"]
    )
    parser.add_argument(
        "pattern",
        nargs="*"
    )
    args = parser.parse_args()

    if args.operation == "get":
       view = view_mapping[args.type]
       get_func = getattr(view, f"get_{args.type}")
       pattern = int(args.pattern[0])
       result = get_func(pattern)
       print(result)
    elif args.operation == "create":
        controller = controller_mapping[args.type]
        create_func = getattr(controller, f"create_{args.type}")
        pattern = args.pattern[0]
        dict_repr = literal_eval(pattern)
        result = create_func(**dict_repr)
        print(result)
    elif args.operation == "update":
        controller = controller_mapping[args.type]
        update_func = getattr(controller, f"update_{args.type}")
        model_id = int(args.pattern[0])
        pattern = args.pattern[1]
        dict_repr = literal_eval(pattern)
        result = update_func(model_id, **dict_repr)
        print(result)
    elif args.operation == "deactivate":
        controller = controller_mapping[args.type]
        deactivate_func = getattr(controller, f"deactivate_{args.type}")
        model_id = int(args.pattern[0])
        result = deactivate_func(model_id)
        print(result)
    elif args.operation == "filter":
        view = view_mapping[args.type]
        filter_func = getattr(view, f"get_{args.type}_filtered")
        filter_pattern = ' '.join(args.pattern)
        result = filter_func(filter_pattern)
        print(result)
