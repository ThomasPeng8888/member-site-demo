Floating contact bottom-right polish

Changes:
- Reduced fixed contact button size for a calmer UI.
- Moved mobile position slightly lower while avoiding overlap with the product mobile LINE inquiry bar.
- Added optional FACEBOOK_MESSENGER_URL / FB_MESSENGER_URL environment variable support.
  If it is set to a direct Messenger URL such as https://m.me/<page_username_or_id>,
  the floating FB button opens Messenger directly.
  If it is not set, the button falls back to the existing Facebook page URL.

No migration is required.
