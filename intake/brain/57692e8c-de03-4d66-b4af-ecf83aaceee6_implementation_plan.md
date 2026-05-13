# Resolve Android Build Issues

The Android build is failing due to an incompatible Java version (JDK 25) and a missing Android SDK configuration. This plan outlines the steps to install JDK 21, locate or set up the Android SDK, and configure the project to use them.

## User Review Required

> [!IMPORTANT]
> - I will be installing `openjdk@21` via Homebrew, which might require your password if it's the first time running brew for a while.
> - I will be creating/modifying `src/mobile/android/local.properties`.

## Proposed Changes

### Environment Configuration

#### [MODIFY] [local.properties](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/mobile/android/local.properties) [NEW]
- Set `sdk.dir` to the identified Android SDK location.

### Dependency Management

#### [MODIFY] [package.json](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/package.json)
- Ensuring `turbo` and `npm` commands are consistent. (Actually, this might not be needed if I just run the commands directly).

## Verification Plan

### Automated Tests
- Run `./gradlew :app:help` in `src/mobile/android` to verify Gradle initialization.
- Run `npm run android` in `src/mobile` to verify the build starts.

### Manual Verification
- Verify that the Android build progresses past the plugin resolution and SDK check phases.
