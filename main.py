class SpaceManager:
    """Manages Confluence space configurations.

    Handles adding new Confluence spaces with associated credentials and update intervals.
    Publishes space configuration to Pulsar.
    """

    def add_new_space(self, space_name, credentials, update_interval):
        pass


class PulsarProducer:
    """Facilitates sending messages to Pulsar.

    Used for publishing various events, such as space additions, updates, and deletions, to Pulsar topics.
    """

    def send_message(self, topic, message):
        pass


class SpaceConsumer:
    """Processes new space configurations from Pulsar.

    Consumes messages from Pulsar related to new space additions and stores configurations in SQLite.
    """

    def consume_message(self):
        pass


class PagePuller:
    """Retrieves pages and their comments from Confluence spaces.

    Activated for newly added spaces or during scheduled updates, it fetches pages along with their comments and posts the data to Pulsar.
    """

    def pull_pages_and_comments(self, space_name):
        pass


class PageConsumer:
    """Handles page data from Pulsar.

    Consumes page data from Pulsar and extracts and stores in the database including metadata (space id, page id, user who created the page, last update date and time) and content (title text, body text, and comment text).
    """

    def consume_page_data(self):
        pass


class UpdateScheduler:
    """Schedules update checks for Confluence spaces.

    Triggers periodic checks for updates and deletions in Confluence spaces based on configured intervals.
    """

    def schedule_updates(self):
        pass


class UpdateProducer:
    """Sends update and delete events to Pulsar.

    Collects updated and deleted page information from Confluence and publishes it to Pulsar.
    """

    def send_update(self, update_info):
        pass


class UpdateConsumer:
    """Processes updates and deletions from Pulsar.

    Listens for update and delete events on Pulsar and updates or removes corresponding pages in SQLite.
    """

    def consume_updates(self):
        pass


class ChromaSync:
    """Syncs page data from Pulsar to Chroma DB.

    Listens to Pulsar topics for page data, including new, updated, and deleted pages, and syncs this data with Chroma DB.
    """

    def sync_with_chroma(self):
        pass
