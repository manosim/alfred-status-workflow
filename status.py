import sys
from workflow import Workflow, web

SERVICES = [
    {
        "code": "GH",
        "service": 'GitHub',
        "valid_aliases": ["github", "gh"],
        "url": "https://status.github.com/api/status.json"
    },
    {
        "code": "TW",
        "service": "Twitter",
        "valid_aliases": ["twitter", "tw"],
        "url": "https://status.github.com/api/status.json"
    }
]


def find_service(query):
    for service in SERVICES:
        if query.lower() in service["valid_aliases"]:
            return service
    return None


def get_status_gh(service):
    # FIXME: Implement Icon
    response = web.get(service["url"]).json()
    status = response["status"]
    icon = "./assets/green.png" if status == "good" else None
    icon = "./assets/minor.png" if status == "minor" else icon
    icon = "./assets/major.png" if status == "major" else icon

    wf.logger.critical(status)

    wf.add_item(
        title=status.capitalize(),
        subtitle=response["last_updated"],
        icon=icon,
        icontype="file"
    )


def get_status_tw(service):
    wf.add_item("Coming soon!")


def get_status(service):
    options = {
        "GH": get_status_gh,
        "TW": get_status_tw
    }

    service_code = service["code"]
    return options[service_code](service)


def main(wf):
    # The Workflow instance will be passed to the function
    # you call from `Workflow.run`. Not so useful, as
    # the `wf` object created in `if __name__ ...` below is global.
    #
    # Your imports go here if you want to catch import errors (not a bad idea)
    # or if the modules/packages are in a directory added via `Workflow(libraries=...)`
    # Get args from Workflow, already in normalized Unicode

    query = " ".join(wf.args) if len(wf.args) > 0 else False
    service = find_service(query)
    if service:
        get_status(service)
    else:
        wf.add_item('Invalid Query', 'Looks like this service is not supported or does not exist.')

    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but Alfred won't be listening
    # any more...
    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow` object
    wf = Workflow()
    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.
    sys.exit(wf.run(main))
