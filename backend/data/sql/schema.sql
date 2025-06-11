CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    "app_info" JSONB,
    "batch_event_index" BIGINT,
    "batch_ordering_id" BIGINT,
    "batch_page_id" BIGINT,
    "collected_traffic_source" JSONB,
    "device" JSONB,
    "ecommerce" JSONB,
    "event_bundle_sequence_id" BIGINT,
    "event_dimensions" JSONB,
    "event_previous_timestamp" BIGINT,
    "event_server_timestamp_offset" BIGINT,
    "event_value_in_usd" FLOAT,
    "geo" JSONB,
    "is_active_user" BOOLEAN,
    "items" JSONB,
    "privacy_info" JSONB,
    "publisher" JSONB,
    "session_traffic_source_last_click" JSONB,
    "traffic_source" JSONB,
    "user_ltv" JSONB,
    "page_location" TEXT,
    "page_referrer" TEXT,
    "page_title" TEXT,
    "screen_name" TEXT,
    "engagement_time_msec" BIGINT,
    "link_url" TEXT,
    "outbound" BOOLEAN,
    "search_term" TEXT,
    "video_title" TEXT,
    "video_provider" TEXT,
    "video_current_time" FLOAT,
    "video_percent" FLOAT,
    "file_name" TEXT,
    "file_extension" TEXT,
    "campaign" TEXT,
    "source" TEXT,
    "medium" TEXT,
    "term" TEXT,
    "content" TEXT,
    "transaction_id" TEXT,
    "value" FLOAT,
    "currency" TEXT,
    "bq_column_page_title" TEXT,
    "bq_column_page_location" TEXT,
    "bq_column_ga_session_id" BIGINT,
    "bq_column_session_engaged" TEXT,
    "bq_column_batch_ordering_id" BIGINT,
    "bq_column_ga_session_number" BIGINT,
    "bq_column_batch_page_id" BIGINT,
    "bq_column_entrances" BIGINT,
    "bq_column_percent_scrolled" FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE app_info (
    id SERIAL PRIMARY KEY,
    parent_id BIGINT NOT NULL REFERENCES events(id),
    "firebase_app_id" TEXT,
    "app_id" TEXT,
    "install_source" TEXT,
    "install_store" TEXT,
    "version" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE collected_traffic_source (
    id SERIAL PRIMARY KEY,
    parent_id BIGINT NOT NULL REFERENCES events(id),
    "dclid" TEXT,
    "gclid" TEXT,
    "manual_campaign_id" TEXT,
    "manual_campaign_name" TEXT,
    "manual_content" TEXT,
    "manual_creative_format" TEXT,
    "manual_marketing_tactic" TEXT,
    "manual_medium" TEXT,
    "manual_source" TEXT,
    "manual_source_platform" TEXT,
    "manual_term" TEXT,
    "srsltid" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE device (
    id SERIAL PRIMARY KEY,
    parent_id BIGINT NOT NULL REFERENCES events(id),
    "advertising_id" TEXT,
    "browser" TEXT,
    "browser_version" TEXT,
    "category" TEXT,
    "is_limited_ad_tracking" TEXT,
    "language" TEXT,
    "mobile_brand_name" TEXT,
    "mobile_marketing_name" TEXT,
    "mobile_model_name" TEXT,
    "mobile_os_hardware_model" TEXT,
    "operating_system" TEXT,
    "operating_system_version" TEXT,
    "time_zone_offset_seconds" BIGINT,
    "vendor_id" TEXT,
    "web_info" JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE web_info (
    id SERIAL PRIMARY KEY,
    parent_id BIGINT NOT NULL REFERENCES device(id),
    "browser" TEXT,
    "browser_version" TEXT,
    "hostname" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ecommerce (
    id SERIAL PRIMARY KEY,
    parent_id BIGINT NOT NULL REFERENCES events(id),
    "purchase_revenue" FLOAT,
    "purchase_revenue_in_usd" FLOAT,
    "refund_value" FLOAT,
    "refund_value_in_usd" FLOAT,
    "shipping_value" FLOAT,
    "shipping_value_in_usd" FLOAT,
    "tax_value" FLOAT,
    "tax_value_in_usd" FLOAT,
    "total_item_quantity" BIGINT,
    "transaction_id" TEXT,
    "unique_items" BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE event_dimensions (
    id SERIAL PRIMARY KEY,
    parent_id BIGINT NOT NULL REFERENCES events(id),
    "hostname" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    parent_id BIGINT NOT NULL REFERENCES events(id),
    "affiliation" TEXT,
    "coupon" TEXT,
    "creative_name" TEXT,
    "creative_slot" TEXT,
    "item_brand" TEXT,
    "item_category" TEXT,
    "item_category2" TEXT,
    "item_category3" TEXT,
    "item_category4" TEXT,
    "item_category5" TEXT,
    "item_id" TEXT,
    "item_list_id" TEXT,
    "item_list_index" TEXT,
    "item_list_name" TEXT,
    "item_name" TEXT,
    "item_params" JSONB,
    "item_refund" FLOAT,
    "item_refund_in_usd" FLOAT,
    "item_revenue" FLOAT,
    "item_revenue_in_usd" FLOAT,
    "item_variant" TEXT,
    "location_id" TEXT,
    "price" FLOAT,
    "price_in_usd" FLOAT,
    "promotion_id" TEXT,
    "promotion_name" TEXT,
    "quantity" BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE item_params (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES items(id),
    "key" TEXT,
    "value" JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE value (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES item_params(id),
    "double_value" FLOAT,
    "float_value" FLOAT,
    "int_value" INT,
    "string_value" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE privacy_info (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES events(id),
    "ads_storage" TEXT,
    "analytics_storage" TEXT,
    "uses_transient_token" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE publisher (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES events(id),
    "ad_format" TEXT,
    "ad_revenue_in_usd" FLOAT,
    "ad_source_name" TEXT,
    "ad_unit_id" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE session_traffic_source_last_click (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES events(id),
    "cm360_campaign" JSONB,
    "cross_channel_campaign" JSONB,
    "dv360_campaign" JSONB,
    "google_ads_campaign" JSONB,
    "manual_campaign" JSONB,
    "sa360_campaign" JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cm360_campaign (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES session_traffic_source_last_click(id),
    "account_id" TEXT,
    "account_name" TEXT,
    "advertiser_id" TEXT,
    "advertiser_name" TEXT,
    "campaign_id" TEXT,
    "campaign_name" TEXT,
    "creative_format" TEXT,
    "creative_id" TEXT,
    "creative_name" TEXT,
    "creative_type" TEXT,
    "creative_type_id" TEXT,
    "creative_version" TEXT,
    "medium" TEXT,
    "placement_cost_structure" TEXT,
    "placement_id" TEXT,
    "placement_name" TEXT,
    "rendering_id" TEXT,
    "site_id" TEXT,
    "site_name" TEXT,
    "source" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cross_channel_campaign (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES session_traffic_source_last_click(id),
    "campaign_id" TEXT,
    "campaign_name" TEXT,
    "default_channel_group" TEXT,
    "medium" TEXT,
    "primary_channel_group" TEXT,
    "source" TEXT,
    "source_platform" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dv360_campaign (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES session_traffic_source_last_click(id),
    "advertiser_id" TEXT,
    "advertiser_name" TEXT,
    "campaign_id" TEXT,
    "campaign_name" TEXT,
    "creative_format" TEXT,
    "creative_id" TEXT,
    "creative_name" TEXT,
    "exchange_id" TEXT,
    "exchange_name" TEXT,
    "insertion_order_id" TEXT,
    "insertion_order_name" TEXT,
    "line_item_id" TEXT,
    "line_item_name" TEXT,
    "medium" TEXT,
    "partner_id" TEXT,
    "partner_name" TEXT,
    "source" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE google_ads_campaign (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES session_traffic_source_last_click(id),
    "account_name" TEXT,
    "ad_group_id" TEXT,
    "ad_group_name" TEXT,
    "campaign_id" TEXT,
    "campaign_name" TEXT,
    "customer_id" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE manual_campaign (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES session_traffic_source_last_click(id),
    "campaign_id" TEXT,
    "campaign_name" TEXT,
    "content" TEXT,
    "creative_format" TEXT,
    "marketing_tactic" TEXT,
    "medium" TEXT,
    "source" TEXT,
    "source_platform" TEXT,
    "term" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sa360_campaign (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES session_traffic_source_last_click(id),
    "ad_group_id" TEXT,
    "ad_group_name" TEXT,
    "campaign_id" TEXT,
    "campaign_name" TEXT,
    "creative_format" TEXT,
    "engine_account_name" TEXT,
    "engine_account_type" TEXT,
    "manager_account_name" TEXT,
    "medium" TEXT,
    "source" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE traffic_source (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES events(id),
    "medium" TEXT,
    "name" TEXT,
    "source" TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_ltv (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES events(id),
    "currency" TEXT,
    "revenue" FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
