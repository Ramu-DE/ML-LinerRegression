# AWS EKS Fundamentals — animated videos

One video per topic, following the folder and file order of `EKS/AWS_EKS_fundamentals/concepts/`. Every video has chapter markers (in VLC: *Playback → Chapter*) and a guide that explains each scene at its timestamp. Measured numbers come from the **[LIVE]** cluster runs in `EXECUTION_SUMMARY.md`.

| # | Video | Length | Chapters | Guide | Drawings | Status |
|---|---|---|---|---|---|---|
| 1 | [EKS-Exposing-Applications.mp4](exposing/EKS-Exposing-Applications.mp4) | 06:11 | Controller pattern & LBC · Service LoadBalancer / NLB · Ingress / ALB · Gateway API | [GUIDE.md](exposing/GUIDE.md) | [.excalidraw](exposing/EKS-Exposing-Applications.excalidraw) | Live (ExternalDNS documented) |
| 2 | [EKS-Storage.mp4](storage/EKS-Storage.mp4) | 12:28 | Storage basics & CSI · EBS · EFS · Mountpoint S3 · S3 Files · FSx OpenZFS · FSx Lustre · FSx ONTAP · Cleanup & choosing | [GUIDE.md](storage/GUIDE.md) | [.excalidraw](storage/EKS-Storage.excalidraw) | Live |
| 3 | [EKS-Compute.mp4](compute/EKS-Compute.mp4) | 09:20 | Managed node groups · Cluster Autoscaler · Graviton · Spot · Karpenter · Fargate | [GUIDE.md](compute/GUIDE.md) | [.excalidraw](compute/EKS-Compute.excalidraw) | Live |
| 4 | [EKS-Networking.mp4](networking/EKS-Networking.mp4) | 08:47 | Pod IPs · Pod communication · Network policies · SG for pods · Custom networking · Prefix delegation · Hybrid nodes | [GUIDE.md](networking/GUIDE.md) | [.excalidraw](networking/EKS-Networking.excalidraw) | Partly live (Auto Mode) |
| 5 | [EKS-Workload-Autoscaling.mp4](workload-autoscaling/EKS-Workload-Autoscaling.mp4) | 05:13 | HPA · CPA · KEDA · Cluster upgrades note | [GUIDE.md](workload-autoscaling/GUIDE.md) | [.excalidraw](workload-autoscaling/EKS-Workload-Autoscaling.excalidraw) | Documented only |

Suggested order: 1 → 2 → 3 → 4 → 5 (the same order as the source README). Each topic folder also contains the individual chapter videos.
