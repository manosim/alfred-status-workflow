import sys
import re
import cgi
import dateutil.parser
import feedparser
from datetime import datetime
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
        "code": "FM",
        "service": "Fast Mail",
        "valid_aliases": ["fm", "fast mail", "fastmail"],
        "url": "http://www.fastmailstatus.com/feed"
    },
    {
        "code": "TRCI",
        "service": "Travis CI",
        "valid_aliases": ["travis", "travis ci", "travisci"],
        "url": "https://www.traviscistatus.com/history.rss"
    },
    {
        "code": "DCKR",
        "service": "Docker",
        "valid_aliases": ["docker", "dckr"],
        "url": "http://status.docker.com/pages/533c6539221ae15e3f000031/rss"
    }
]


def remove_html(text):
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')

    # Remove well-formed tags, fixing mistakes by legitimate users
    no_tags = tag_re.sub('', text)

    # Clean up anything else by escaping
    ready_for_web = cgi.escape(no_tags)
    return ready_for_web


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


def get_status_fm(service):
    response = feedparser.parse(service["url"])

    for item in response.entries:
        status = item.title.split(" - ")[-1]
        date = datetime(*item.published_parsed[:6])

        icon = ICON_STATUS_GOOD if status == "Up" else None
        icon = ICON_STATUS_MINOR if status == "Warning" else icon
        icon = ICON_STATUS_MAJOR if status == "Down" else icon

        wf.add_item(
            title=status.capitalize(),
            subtitle=date.strftime('%d %B %Y - ') + item.description,
            icon=icon,
            icontype="file"
        )


def get_status_docker(service):
    response = feedparser.parse(service["url"])

    for item in response.entries:

        status = item.title.split(" - ")[-1]
        date = datetime(*item.published_parsed[:6])

        icon = ICON_STATUS_GOOD if status == "Up" else None
        icon = ICON_STATUS_MINOR if status == "Warning" else icon
        icon = ICON_STATUS_MAJOR if status == "Down" else icon

        wf.add_item(
            title=status.capitalize(),
            subtitle=date.strftime('%d %B %Y - ') + item.description,
            icon=icon,
            icontype="file"
        )


def get_status_trci(service):
    response = feedparser.parse(service["url"])

    for item in response.entries:
        status = remove_html(item.description).split(" - ")[0].split("UTC")[-1]
        date = datetime(*item.published_parsed[:6])

        icon = ICON_STATUS_GOOD if status == "Resolved" else None
        icon = ICON_STATUS_GOOD if status == "Completed" else icon
        icon = ICON_STATUS_GOOD if status == "Scheduled" else icon
        icon = ICON_STATUS_MINOR if status == "In progress" else icon
        icon = ICON_STATUS_MINOR if status == "Identified" else icon
        icon = ICON_STATUS_MINOR if status == "Update" else icon
        icon = ICON_STATUS_MINOR if status == "Monitoring" else icon
        icon = ICON_STATUS_MAJOR if status == "Down" else icon

        wf.add_item(
            title=status.capitalize(),
            subtitle=date.strftime('%d %B %Y - ') + remove_html(item.description).split(" - ")[-1],
            icon=icon,
            icontype="file"
        )


def get_status(service):
    options = {
        "GH": get_status_gh,
        "FM": get_status_fm,
        "TRCI": get_status_trci,
        "DCKR": get_status_docker
    }

    service_code = service["code"]
    return options[service_code](service)


def main(wf):
    # The Workflow instance will be passed to the function
    # you call from `Workflow.run`. Not so useful, as
    # the `wf` object created in `if __name__ ...` below is global.

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
