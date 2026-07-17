; VoidTorrent Installer - NSIS script
; Builds VoidTorrent-1.0.0-x64-setup.exe from the PyInstaller dist folder.
;
; Usage (with NSIS installed):
;   makensis /DVERSION=1.0.0 voidtorrent.nsi
;
; Expected layout (relative to this script):
;   ../build/dist/VoidTorrent.exe     (PyInstaller output)
;   ../assets/voidtorrent.ico         (installer icon)
;   ../LICENSE / README               (optional extras)

!define APPNAME "VoidTorrent"
!define VERSION "1.0.0"
!define PUBLISHER "VoidTorrent"
!define WEBSITE "https://voidtorrent.example"

; ---- NSIS includes ----
!include "MUI2.nsh"
!include "FileFunc.nsh"

; ---- Installer attributes ----
Name "${APPNAME} ${VERSION}"
OutFile "VoidTorrent-${VERSION}-x64-setup.exe"
InstallDir "$LOCALAPPDATA\${APPNAME}"
InstallDirRegKey HKCU "Software\${APPNAME}" "InstallDir"
RequestExecutionLevel user
ManifestDPIAware true

!ifdef ICON
  Icon "${ICON}"
  UninstallIcon "${ICON}"
!else
  Icon "../assets/voidtorrent.ico"
  UninstallIcon "../assets/voidtorrent.ico"
!endif

; ---- UI ----
!define MUI_ABORTWARNING
!define MUI_ICON "../assets/voidtorrent.ico"
!define MUI_UNICON "../assets/voidtorrent.ico"
!define MUI_WELCOMEPAGE_TITLE "Welcome to ${APPNAME}"
!define MUI_WELCOMEPAGE_TEXT "VoidTorrent is a free, open-source, ad-free BitTorrent client for Windows. This wizard will install it on your computer."
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\VoidTorrent.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APPNAME} now"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ---- Version info ----
VIProductVersion "${VERSION}.0"
VIAddVersionKey "ProductName" "${APPNAME}"
VIAddVersionKey "ProductVersion" "${VERSION}"
VIAddVersionKey "CompanyName" "${PUBLISHER}"
VIAddVersionKey "LegalCopyright" "(c) 2026 ${PUBLISHER}"
VIAddVersionKey "FileVersion" "${VERSION}.0"
VIAddVersionKey "FileDescription" "${APPNAME} BitTorrent Client"

Section "Install" SecInstall
  SetOutPath "$INSTDIR"
  File /r "..\build\dist\VoidTorrent.exe"

  ; Start menu shortcut
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\VoidTorrent.exe" "" "$INSTDIR\VoidTorrent.exe" 0
  CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk" "$INSTDIR\Uninstall.exe"

  ; Optional desktop shortcut
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\VoidTorrent.exe" "" "$INSTDIR\VoidTorrent.exe" 0

  ; Uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\${APPNAME}" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\VoidTorrent.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${PUBLISHER}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${WEBSITE}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
SectionEnd

Section "Uninstall" SecUninstall
  Delete "$INSTDIR\VoidTorrent.exe"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  Delete "$DESKTOP\${APPNAME}.lnk"
  DeleteRegKey HKCU "Software\${APPNAME}"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
