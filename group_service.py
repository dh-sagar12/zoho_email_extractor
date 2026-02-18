import json
import os
from collections import defaultdict


class GroupService:
    ALLOWED_FIELDS = {
        "sentDateInGMT",
        "subject",
        "messageId",
        "priority",
        "toAddress",
        "ccAddress",
        "threadId",
        "sender",
        "fromAddress",
        "content",
        "attachments",
    }

    def __init__(
        self,
        input_file="messages_with_content.json",
        output_file="grouped_messages_with_content.json",
        save_chunk_size=500,
    ):
        self.input_file = input_file
        self.output_file = output_file
        self.save_chunk_size = save_chunk_size

    def load_existing_output(self):
        """Load previously saved grouped output (if exists)."""
        if os.path.exists(self.output_file):
            with open(self.output_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def filter_message_fields(self, message):
        """Extract only ALLOWED_FIELDS from a message."""
        filtered = {key: message[key] for key in self.ALLOWED_FIELDS if key in message}

        # Ensure attachments is always an array
        if "attachments" in message and isinstance(message["attachments"], list):
            filtered["attachments"] = message["attachments"]

        return filtered

    def save_progress(self, grouped_messages):
        """Save grouped output to file."""
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(grouped_messages, f, indent=4)
        print("✅ Progress saved.")

    def process_messages(self):
        """Main processing method: group, filter, sort, save (chunked)."""

        with open(self.input_file, "r", encoding="utf-8") as f:
            messages = json.load(f)

        grouped_messages = self.load_existing_output()

        count = 0

        for msg in messages:
            thread_id = msg.get("threadId", "UNKNOWN_THREAD")

            if thread_id not in grouped_messages:
                grouped_messages[thread_id] = []

            grouped_messages[thread_id].append(self.filter_message_fields(msg))
            count += 1

            # Checkpoint save
            if count % self.save_chunk_size == 0:
                print(f"Processed {count} messages... checkpointing.")
                self.save_progress(grouped_messages)

        print(f"Processing complete ({count} messages). Sorting...")

        # Sort each thread by sentDateInGMT
        for thread_id in grouped_messages:
            grouped_messages[thread_id] = sorted(
                grouped_messages[thread_id], key=lambda m: int(m["sentDateInGMT"])
            )

        self.save_progress(grouped_messages)
        print("🎉 Finished: grouped, sorted, filtered, saved.")


# Run directly
if __name__ == "__main__":
    service = GroupService()
    service.process_messages()
