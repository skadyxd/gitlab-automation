MESSAGES = {
    "merge_request_fetch_error": "Error fetching merge requests for user {user_id}: {status}",

    "merge_request_not_approved": "MR {mr_link} is not approved",

    "merge_request_invalid_approver": "MR {mr_link} is not approved by a valid approver",

    "pipeline_fetch_error": "Error fetching pipelines for MR link {mr_link}: {status}",

    "pipeline_unsuccessful": "MR {mr_link} has unsuccessful pipeline: {pipeline_status}",

    "pipeline_failed_message": '''❌ Pipelines failed for **MR {mr_title}!**
**MR link:** <{mr_link}>
**JIRA:** __<{jira_link}>__
**Author:** <@{user_id_discord}>
**Target branch:** {target_branch}''',


    "merge_successful": '''✅ Merge request merged!

**MR title**: {mr_title}
**MR link:** <{mr_link}>
**JIRA:** __<{jira_link}>__
**Author:** <@{user_id_discord}>
**Target branch:** {target_branch}''',


    "merge_failed": '''❌ Merge request failed!

**MR title**: {mr_title}
**MR link:** <{mr_link}>
**JIRA:** __<{jira_link}>__
**Author:** <@{user_id_discord}>
**Target branch:** {target_branch}'''
}
