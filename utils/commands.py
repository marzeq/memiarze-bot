from discord.ext.commands import Group


def get_command_usage(command):
    if command.usage:
        return command.usage

    joined_aliases = "|".join(command.aliases)
    if joined_aliases:
        name_w_aliases = f"[{command.name}|{joined_aliases}]"
    else:
        name_w_aliases = command.name

    if type(command) == Group:
        to_return = name_w_aliases + "\n"

        for sub_command in command.commands:
            to_return += f"\t{get_command_usage(sub_command)}\n"

        return to_return

    return f"{name_w_aliases} {command.signature}"
