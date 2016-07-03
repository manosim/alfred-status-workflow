import sys
import dateutil.parser
from workflow import Workflow, web

ICON_STATUS_GOOD = "./assets/green.png"
ICON_STATUS_MINOR = "./assets/minor.png"
ICON_STATUS_MAJOR = "./assets/major.png"

UPDATE_SETTINGS = {
    "github_slug": "ekonstantinidis/alfred-status-workflow"
}
HELP_URL = 'https://github.com/ekonstantinidis/alfred-status-workflow/issues'

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
    response = web.get(service["url"]).json()
    status = response["status"]
    date = dateutil.parser.parse(response["last_updated"])

    icon = ICON_STATUS_GOOD if status == "good" else None
    icon = ICON_STATUS_MINOR if status == "minor" else icon
    icon = ICON_STATUS_MAJOR if status == "major" else icon

    wf.add_item(
        title=status.capitalize(),
        subtitle=date.strftime('Last updated on %d %B %Y'),
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

    # Auto Update
    if wf.update_available:
        wf.add_item(
            title="Update available!",
            subtitle="Action this item to install the update",
            autocomplete="workflow:update"
        )

    query = " ".join(wf.args) if len(wf.args) > 0 else False
    service = find_service(query)
    if service:
        get_status(service)
    else:
        wf.add_item('Invalid Service', 'Looks like this service is not supported or does not exist.')

    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but Alfred won't be listening
    # any more...
    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow` object
    wf = Workflow(
        update_settings=UPDATE_SETTINGS,
        help_url=HELP_URL
    )
    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.
    sys.exit(wf.run(main))
