# Demo Script: Cloud-based System Resource Monitoring Dashboard

**Length:** about 8 minutes. `TODO(team)`: confirm the time limit for the presentation.
**Order (from the project plan):** normal monitoring → stress test → resulting alert → history chart.

## Before the demo (check 15 minutes ahead)

- [ ] All 3 VMs are running. `systemctl status monitor-api` on the server shows it active.
- [ ] Collectors are running on vm1 and vm2. Both show recent data in `GET /vms`.
- [ ] Dashboard is open in a browser at projector resolution, zoomed so it's readable from the back.
- [ ] An SSH session to vm1 is open in a second window with the stress-ng command typed but **not run**.
- [ ] Email inbox or Slack channel is open in a third window for the notification.
- [ ] At least an hour of history has been collected, so the history chart has data.
- [ ] Backup demo video is downloaded locally (don't stream it).

## Script

| # | Time | Who | Screen | What to say / do |
|---|---|---|---|---|
| 1 | 0:00 | `TODO` | Slides: architecture | "We built a dashboard that monitors CPU, memory, disk and uptime across Linux VMs. A Python collector on each VM sends readings to our REST API, which stores them in SQL and checks them against thresholds." |
| 2 | 1:00 | `TODO` | Dashboard: VM list | **Normal monitoring.** Point out both VMs, their current stats and the auto-refresh. "Everything is under threshold, so nothing is highlighted." |
| 3 | 2:00 | `TODO` | Dashboard: thresholds | Show the defaults (CPU 80%, memory 85%, disk 90%) and that they can be changed through the dashboard or `PUT /thresholds`. |
| 4 | 2:45 | `TODO` | SSH to vm1 | **Stress test.** Run `stress-ng --cpu 0 --cpu-load 95 --timeout 120s`. "This pushes vm1's CPU above 80%." |
| 5 | 3:00 | `TODO` | Dashboard | Watch vm1's CPU climb. While waiting, explain: the collector reports every 10–30 seconds and the API checks each reading as it arrives. |
| 6 | 3:45 | `TODO` | Dashboard: alerts panel | **Resulting alert.** vm1 is highlighted and a new alert appears in the panel. |
| 7 | 4:15 | `TODO` | Email / Slack | Show the notification that arrived. |
| 8 | 4:45 | `TODO` | Dashboard: history chart | **History chart.** Open vm1's chart and switch between 1 h, 24 h and 7 d. The CPU spike from step 4 is visible. |
| 9 | 5:45 | `TODO` | Dashboard | Stress test ends. CPU drops back to normal. |
| 10 | 6:15 | `TODO` | Slides: results / wrap-up | Summary, what we'd add next, then questions. |

## If something fails

| Problem | What to do |
|---|---|
| Dashboard won't load | Show that it displays the "API unavailable" message (a planned feature), then switch to the backup video. |
| Alert doesn't appear within ~90 seconds | Keep talking through the history chart. If there's still nothing, play the alert section of the backup video. |
| Notification is slow | Move on and come back to the inbox at the end. |
| VM is unreachable | Play the backup video from the start and narrate over it. |

## Backup video

Record the full script above (steps 2–9) with narration. Save it locally and in the shared drive. `TODO(JG)`: add the link once it's recorded (by Dec 1).
