MESSAGES = {
    "merge_request_fetch_error": "Error fetching merge requests for user {user_id}: {status}",

    "merge_request_not_approved": "MR {mr_id} is not approved",

    "merge_request_invalid_approver": "MR {mr_id} is not approved by a valid approver",

    "pipeline_fetch_error": "Error fetching pipelines for MR {mr_id}: {status}",

    "pipeline_unsuccessful": "MR {mr_id} has unsuccessful pipeline: {pipeline_status}",

    "pipeline_failed_message": '''❌ Pipelines failed for **MR {mr_title}!**

**MR ID:** {mr_id}

**Author:** {author_name}

**Target branch:** {target_branch}

Failed Pipelines:
{failure_messages}''',


    "merge_successful": '''✅ Merge request merged!

**MR title**: {mr_title}

**MR ID:**  {mr_id}

**Author:** {author_name}

**Target branch:**  {target_branch}''',


    "merge_failed": '''❌ Merge request failed!

**MR title**: {mr_title}

**MR ID:**  {mr_id}

**Author:** {author_name}

**Target branch:**  {target_branch}'''
}
