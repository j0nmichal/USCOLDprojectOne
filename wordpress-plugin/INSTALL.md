# US Cold Facilities Plugin — Install Guide

## 1. Upload the plugin to GoDaddy

In GoDaddy's WordPress admin (uscold.com/wp-admin):

1. Go to **Plugins → Add New → Upload Plugin**
2. Zip the `uscold-facilities` folder:
   ```
   zip -r uscold-facilities.zip uscold-facilities/
   ```
3. Upload the zip and click **Install Now**, then **Activate**

On activation the plugin creates the `wp_uscold_facilities` table in your database automatically.

---

## 2. Add the API key to wp-config.php

The API key protects all write operations (create, update, delete).
It never appears in any file pushed to GitHub.

In GoDaddy's File Manager (or via SSH if available), open `wp-config.php`
and add this line **above** the `/* That's all, stop editing! */` comment:

```php
define( 'USCOLD_API_KEY', 'REPLACE_WITH_YOUR_SECRET_KEY' );
```

Generate a strong key — something like a 40-character random string.
Keep a copy somewhere safe (1Password, etc.).

---

## 3. Verify the endpoint is live

Open this URL in a browser (should return `[]` until data is loaded):

```
https://uscold.com/wp-json/uscold/v1/facilities
```

---

## 4. Update the local admin

In `uscold-admin.html`, replace the Supabase URL and key with:

- **API base URL:** `https://uscold.com/wp-json/uscold/v1`
- **Header:** `X-USCOLD-Key: YOUR_SECRET_KEY`

(Claude will handle this code change — just confirm the key first.)

---

## 5. Migrate data from Supabase

Once the endpoint is live, Claude can export all 39 facilities from Supabase
and POST them to the new endpoint in one script run.

---

## REST API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/wp-json/uscold/v1/facilities` | None | All published facilities |
| POST | `/wp-json/uscold/v1/facilities` | API key | Create a facility |
| PUT/PATCH | `/wp-json/uscold/v1/facilities/{id}` | API key | Update a facility |
| DELETE | `/wp-json/uscold/v1/facilities/{id}` | API key | Delete a facility |

**Auth header:** `X-USCOLD-Key: your-secret-key`
