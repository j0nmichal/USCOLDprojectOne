<?php
/**
 * Plugin Name: US Cold Facilities
 * Plugin URI:  https://uscold.com
 * Description: Manages US Cold facility data and exposes a REST API for the
 *              location finder, chat interface, and (Phase 2) mobile app.
 * Version:     1.0.0
 * Author:      US Cold
 * License:     Private — not for distribution
 */

defined( 'ABSPATH' ) || exit;

// ── Constants ─────────────────────────────────────────────────────────────────

define( 'USCOLD_VERSION', '1.0.0' );
define( 'USCOLD_TABLE',   'uscold_facilities' );   // no WP prefix yet — added at runtime

// ── Activation: create table ──────────────────────────────────────────────────

register_activation_hook( __FILE__, 'uscold_create_table' );

function uscold_create_table(): void {
    global $wpdb;
    $table   = $wpdb->prefix . USCOLD_TABLE;
    $charset = $wpdb->get_charset_collate();

    // dbDelta is safe to run multiple times — it only alters, never destroys.
    $sql = "CREATE TABLE {$table} (
        id                        INT UNSIGNED   NOT NULL AUTO_INCREMENT,
        created_at                DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at                DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

        -- Identity
        name                      VARCHAR(120)   NOT NULL DEFAULT '',
        city                      VARCHAR(80)    NOT NULL DEFAULT '',
        state                     VARCHAR(50)    NOT NULL DEFAULT '',
        region                    VARCHAR(30)             DEFAULT NULL,
        address                   VARCHAR(160)            DEFAULT NULL,
        zip                       VARCHAR(20)             DEFAULT NULL,

        -- Contact
        phone                     VARCHAR(30)             DEFAULT NULL,
        contact_email             VARCHAR(120)            DEFAULT NULL,

        -- Capacity & Temperature
        pallet_positions          INT UNSIGNED            DEFAULT NULL,
        square_footage            INT UNSIGNED            DEFAULT NULL,
        temp_min_f                SMALLINT                DEFAULT NULL,
        temp_max_f                SMALLINT                DEFAULT NULL,
        dock_doors                SMALLINT UNSIGNED       DEFAULT NULL,
        drop_lot_spaces           SMALLINT UNSIGNED       DEFAULT NULL,

        -- Capabilities
        rail_access               TINYINT(1)     NOT NULL DEFAULT 0,
        rail_carrier              VARCHAR(80)             DEFAULT NULL,
        quick_freeze              TINYINT(1)     NOT NULL DEFAULT 0,
        quick_freeze_auto         TINYINT(1)     NOT NULL DEFAULT 0,
        automated                 TINYINT(1)     NOT NULL DEFAULT 0,
        layer_pick                TINYINT(1)     NOT NULL DEFAULT 0,
        repack                    TINYINT(1)     NOT NULL DEFAULT 0,
        export_import             TINYINT(1)     NOT NULL DEFAULT 0,
        organic                   TINYINT(1)     NOT NULL DEFAULT 0,
        dedicated                 TINYINT(1)     NOT NULL DEFAULT 0,

        -- Services / Flags
        drop_lot                  TINYINT(1)     NOT NULL DEFAULT 0,
        coldshare                 TINYINT(1)     NOT NULL DEFAULT 0,
        freight                   TINYINT(1)     NOT NULL DEFAULT 0,
        phenix_ewms               TINYINT(1)     NOT NULL DEFAULT 0,

        -- Certifications
        brcgs                     TINYINT(1)     NOT NULL DEFAULT 0,
        usda                      TINYINT(1)     NOT NULL DEFAULT 0,
        fda                       TINYINT(1)     NOT NULL DEFAULT 0,
        sqf                       TINYINT(1)     NOT NULL DEFAULT 0,

        -- Status
        published                 TINYINT(1)     NOT NULL DEFAULT 1,
        space_available           TINYINT(1)              DEFAULT NULL,
        expansion                 VARCHAR(30)             DEFAULT NULL,

        -- Media & Notes
        image_url                 TEXT                    DEFAULT NULL,
        notes                     TEXT                    DEFAULT NULL,

        -- Warehouse Contact
        warehouse_contact_name    VARCHAR(120)            DEFAULT NULL,
        warehouse_contact_email   VARCHAR(120)            DEFAULT NULL,
        warehouse_contact_phone   VARCHAR(30)             DEFAULT NULL,

        -- General Manager
        gm_name                   VARCHAR(120)            DEFAULT NULL,
        gm_email                  VARCHAR(120)            DEFAULT NULL,
        gm_phone                  VARCHAR(30)             DEFAULT NULL,

        -- Sales Contact
        sales_contact_name        VARCHAR(120)            DEFAULT NULL,
        sales_contact_email       VARCHAR(120)            DEFAULT NULL,
        sales_contact_phone       VARCHAR(30)             DEFAULT NULL,

        PRIMARY KEY (id),
        KEY idx_published (published),
        KEY idx_region    (region),
        KEY idx_state     (state)
    ) {$charset};";

    require_once ABSPATH . 'wp-admin/includes/upgrade.php';
    dbDelta( $sql );

    update_option( 'uscold_db_version', USCOLD_VERSION );
}

// ── REST API registration ─────────────────────────────────────────────────────

add_action( 'rest_api_init', 'uscold_register_routes' );

function uscold_register_routes(): void {
    $ns = 'uscold/v1';

    // GET  /wp-json/uscold/v1/facilities          — public, all published facilities
    register_rest_route( $ns, '/facilities', [
        'methods'             => WP_REST_Server::READABLE,
        'callback'            => 'uscold_get_facilities',
        'permission_callback' => '__return_true',
    ] );

    // POST /wp-json/uscold/v1/facilities          — create (API key required)
    register_rest_route( $ns, '/facilities', [
        'methods'             => WP_REST_Server::CREATABLE,
        'callback'            => 'uscold_create_facility',
        'permission_callback' => 'uscold_check_api_key',
    ] );

    // PUT|PATCH /wp-json/uscold/v1/facilities/{id} — update (API key required)
    register_rest_route( $ns, '/facilities/(?P<id>\d+)', [
        'methods'             => 'PUT, PATCH',
        'callback'            => 'uscold_update_facility',
        'permission_callback' => 'uscold_check_api_key',
        'args'                => [
            'id' => [ 'validate_callback' => fn( $v ) => is_numeric( $v ) && $v > 0 ],
        ],
    ] );

    // DELETE /wp-json/uscold/v1/facilities/{id}   — delete (API key required)
    register_rest_route( $ns, '/facilities/(?P<id>\d+)', [
        'methods'             => WP_REST_Server::DELETABLE,
        'callback'            => 'uscold_delete_facility',
        'permission_callback' => 'uscold_check_api_key',
        'args'                => [
            'id' => [ 'validate_callback' => fn( $v ) => is_numeric( $v ) && $v > 0 ],
        ],
    ] );
}

// ── Authentication ────────────────────────────────────────────────────────────

/**
 * Reads X-USCOLD-Key from the request header and compares it to the constant
 * defined in wp-config.php:
 *   define( 'USCOLD_API_KEY', 'your-secret-key-here' );
 */
function uscold_check_api_key( WP_REST_Request $request ): bool {
    if ( ! defined( 'USCOLD_API_KEY' ) || USCOLD_API_KEY === '' ) {
        return false; // no key configured — lock down writes
    }
    return hash_equals( USCOLD_API_KEY, (string) $request->get_header( 'X-USCOLD-Key' ) );
}

// ── CORS ──────────────────────────────────────────────────────────────────────
// Allow the location finder (any origin) and the future phone app to read data.
// Write endpoints also pass CORS so the local admin HTML can reach them.

add_action( 'rest_pre_serve_request', function ( $served, $result, $request ) {
    if ( str_starts_with( $request->get_route(), '/uscold/v1/' ) ) {
        header( 'Access-Control-Allow-Origin: *' );
        header( 'Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS' );
        header( 'Access-Control-Allow-Headers: Content-Type, X-USCOLD-Key' );
    }
    return $served;
}, 10, 3 );

// Handle OPTIONS preflight so browsers don't block the request
add_action( 'init', function () {
    if ( isset( $_SERVER['REQUEST_METHOD'] ) && $_SERVER['REQUEST_METHOD'] === 'OPTIONS' ) {
        $uri = $_SERVER['REQUEST_URI'] ?? '';
        if ( str_contains( $uri, '/wp-json/uscold/' ) ) {
            header( 'Access-Control-Allow-Origin: *' );
            header( 'Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS' );
            header( 'Access-Control-Allow-Headers: Content-Type, X-USCOLD-Key' );
            header( 'HTTP/1.1 204 No Content' );
            exit;
        }
    }
} );

// ── Field list (single source of truth) ──────────────────────────────────────

function uscold_fields(): array {
    return [
        'name', 'city', 'state', 'region', 'address', 'zip',
        'phone', 'contact_email',
        'pallet_positions', 'square_footage', 'temp_min_f', 'temp_max_f', 'dock_doors',
        'rail_access', 'rail_carrier', 'quick_freeze', 'quick_freeze_auto',
        'automated', 'layer_pick', 'repack', 'export_import', 'organic', 'dedicated',
        'drop_lot', 'drop_lot_spaces', 'coldshare', 'freight', 'phenix_ewms',
        'brcgs', 'usda', 'fda', 'sqf',
        'published', 'space_available', 'expansion',
        'image_url', 'notes',
        'warehouse_contact_name', 'warehouse_contact_email', 'warehouse_contact_phone',
        'gm_name', 'gm_email', 'gm_phone',
        'sales_contact_name', 'sales_contact_email', 'sales_contact_phone',
    ];
}

// ── Type casting ──────────────────────────────────────────────────────────────

function uscold_cast( array $row ): array {
    $bool_fields = [
        'rail_access', 'quick_freeze', 'quick_freeze_auto', 'automated', 'layer_pick',
        'repack', 'export_import', 'organic', 'dedicated',
        'drop_lot', 'drop_lot_spaces', 'coldshare', 'freight', 'phenix_ewms',
        'brcgs', 'usda', 'fda', 'sqf', 'published',
    ];
    $nullable_bool_fields = [ 'space_available' ];
    $int_fields = [ 'id', 'pallet_positions', 'square_footage', 'temp_min_f', 'temp_max_f', 'dock_doors', 'drop_lot_spaces' ];

    foreach ( $bool_fields as $k ) {
        if ( array_key_exists( $k, $row ) ) {
            $row[ $k ] = (bool) (int) $row[ $k ];
        }
    }
    foreach ( $nullable_bool_fields as $k ) {
        if ( array_key_exists( $k, $row ) ) {
            $row[ $k ] = $row[ $k ] !== null ? (bool) (int) $row[ $k ] : null;
        }
    }
    foreach ( $int_fields as $k ) {
        if ( array_key_exists( $k, $row ) ) {
            $row[ $k ] = $row[ $k ] !== null ? (int) $row[ $k ] : null;
        }
    }

    return $row;
}

// ── Sanitize incoming body ────────────────────────────────────────────────────

function uscold_sanitize_body( array $body ): array {
    $allowed = uscold_fields();
    $data    = [];

    foreach ( $allowed as $field ) {
        if ( ! array_key_exists( $field, $body ) ) continue;
        $val = $body[ $field ];
        // Treat empty string as NULL for optional fields
        $data[ $field ] = ( $val === '' ) ? null : $val;
    }

    return $data;
}

// ── GET /facilities ───────────────────────────────────────────────────────────

function uscold_get_facilities(): WP_REST_Response {
    global $wpdb;
    $table = $wpdb->prefix . USCOLD_TABLE;
    $rows  = $wpdb->get_results(
        "SELECT * FROM {$table} WHERE published = 1 ORDER BY name ASC",
        ARRAY_A
    );

    if ( $wpdb->last_error ) {
        return new WP_REST_Response( [ 'error' => $wpdb->last_error ], 500 );
    }

    return new WP_REST_Response( array_map( 'uscold_cast', $rows ?: [] ), 200 );
}

// ── POST /facilities ──────────────────────────────────────────────────────────

function uscold_create_facility( WP_REST_Request $request ): WP_REST_Response {
    global $wpdb;
    $table = $wpdb->prefix . USCOLD_TABLE;
    $data  = uscold_sanitize_body( $request->get_json_params() ?: [] );

    if ( empty( $data['name'] ) ) {
        return new WP_REST_Response( [ 'error' => 'name is required' ], 400 );
    }

    $wpdb->insert( $table, $data );

    if ( $wpdb->last_error ) {
        return new WP_REST_Response( [ 'error' => $wpdb->last_error ], 500 );
    }

    $new = $wpdb->get_row(
        $wpdb->prepare( "SELECT * FROM {$table} WHERE id = %d", $wpdb->insert_id ),
        ARRAY_A
    );

    return new WP_REST_Response( uscold_cast( $new ), 201 );
}

// ── PUT|PATCH /facilities/{id} ────────────────────────────────────────────────

function uscold_update_facility( WP_REST_Request $request ): WP_REST_Response {
    global $wpdb;
    $table = $wpdb->prefix . USCOLD_TABLE;
    $id    = (int) $request->get_param( 'id' );
    $data  = uscold_sanitize_body( $request->get_json_params() ?: [] );

    if ( empty( $data ) ) {
        return new WP_REST_Response( [ 'error' => 'No valid fields supplied' ], 400 );
    }

    $result = $wpdb->update( $table, $data, [ 'id' => $id ] );

    if ( $result === false ) {
        return new WP_REST_Response( [ 'error' => $wpdb->last_error ], 500 );
    }

    $updated = $wpdb->get_row(
        $wpdb->prepare( "SELECT * FROM {$table} WHERE id = %d", $id ),
        ARRAY_A
    );

    if ( ! $updated ) {
        return new WP_REST_Response( [ 'error' => 'Facility not found' ], 404 );
    }

    return new WP_REST_Response( uscold_cast( $updated ), 200 );
}

// ── DELETE /facilities/{id} ───────────────────────────────────────────────────

function uscold_delete_facility( WP_REST_Request $request ): WP_REST_Response {
    global $wpdb;
    $table  = $wpdb->prefix . USCOLD_TABLE;
    $id     = (int) $request->get_param( 'id' );
    $result = $wpdb->delete( $table, [ 'id' => $id ] );

    if ( $result === false ) {
        return new WP_REST_Response( [ 'error' => $wpdb->last_error ], 500 );
    }

    return new WP_REST_Response( [ 'deleted' => true, 'id' => $id ], 200 );
}
