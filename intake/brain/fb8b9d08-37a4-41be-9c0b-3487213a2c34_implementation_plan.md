# Resolution Plan: Persistent Plugin Error & Environment Setup

The IDE is still reporting a resolution error with `25.0.1` (JDK 25) because it is likely using a cached Gradle daemon or its own JDK settings that haven't updated to pick up the `org.gradle.java.home` fix in `gradle.properties`.

Additionally, the user has requested the installation of Android Studio.

## User Review Required

> [!IMPORTANT]
> You may need to manually trigger a Gradle sync in your IDE after I complete these steps.
> - **VS Code**: Run command `Gradle: Refresh Gradle Projects`
> - **Android Studio**: Click `Sync Project with Gradle Files` (elephant icon)

## Proposed Changes

### Android Configuration

#### [MODIFY] [gradle.properties](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/mobile/android/gradle.properties)
Confirm and ensure the `org.gradle.java.home` setting is robust. I will also add a `local.properties` file with a placeholder or attempt to locate the SDK to stop the subsequent "SDK location not found" error. (Completed)

### Software Installation

#### [NEW] Android Studio
I will install Android Studio using Homebrew Cask to provide the necessary IDE for Android development and emulation.

## Verification Plan

### Automated Tests
1. **Kill Daemons**: Run `./gradlew --stop` to kill any hanging daemons using JDK 25. (Completed)
2. **Terminal Sync**: Run `./gradlew tasks --info` and verify `JAVA_VERSION=21.0.10` appears in the logs. (Completed)
3. **Dry Run**: Run `./gradlew :app:assembleDebug --dry-run` to ensure the entire dependency tree resolves. (Completed)
4. **App Verification**: Verify that `Android Studio.app` exists in `/Applications`.

### Manual Verification
- Ask the user to check if the red squiggles/errors disappear in the IDE after the daemon stop and refresh.
- Ask the user to launch Android Studio and perform a Gradle sync.
