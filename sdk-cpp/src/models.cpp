#include "errorbrain/models.h"

namespace ErrorBrain {

// ErrorReport to JSON conversion
json ErrorReport::to_json() const {
    json j;
    j["language"] = language_;
    j["project"] = project_;
    j["message"] = message_;
    j["store_in_vault"] = store_in_vault_;

    if (traceback_) {
        j["traceback"] = *traceback_;
    }

    if (!tags_.empty()) {
        j["tags"] = tags_;
    }

    if (metadata_) {
        j["metadata"] = *metadata_;
    }

    return j;
}

// ErrorResponse constructor from JSON
ErrorResponse::ErrorResponse(const json& j)
    : id_(j.at("id")),
      project_(j.at("project")),
      language_(j.at("language")),
      tags_(j.at("tags").get<std::vector<std::string>>()),
      created_at_(j.at("created_at")),
      explanation_(j.at("explanation")) {
    if (j.contains("saved_path") && !j["saved_path"].is_null()) {
        saved_path_ = j["saved_path"].get<std::string>();
    }
}

// HealthResponse constructor from JSON
HealthResponse::HealthResponse(const json& j)
    : status_(j.at("status")),
      llm_configured_(j.at("llm_configured")),
      vault_configured_(j.at("vault_configured")) {
    if (j.contains("vault_path") && !j["vault_path"].is_null()) {
        vault_path_ = j["vault_path"].get<std::string>();
    }
}

} // namespace ErrorBrain
