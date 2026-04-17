#define MyAppName "AI Drowsiness Detection"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Dharnesh Priyan J"
#define MyAppURL "https://github.com/dharneshpriyan"
#define MyAppExeName "AI Drowsiness Detection.exe"
#define MySourceDir "C:\Users\acer\Desktop\AI Drowsiness Detection\dist\AI Drowsiness Detection"
#define MyProjectDir "C:\Users\acer\Desktop\AI Drowsiness Detection"
#define MyIconFile "C:\Users\acer\Desktop\AI Drowsiness Detection\assets\ds.ico"
#define MyLicenseFile "C:\Users\acer\Desktop\AI Drowsiness Detection\license.txt"
#define MyOutputDir "C:\Users\acer\Desktop\AI Drowsiness Detection\installer_output"

[Setup]
AppId={{8E2E1E74-8D3B-4C32-9D6E-AIDROWSINESS2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
LicenseFile={#MyLicenseFile}
OutputDir={#MyOutputDir}
OutputBaseFilename=AI_Drowsiness_Detection_Setup_v{#MyAppVersion}
SetupIconFile={#MyIconFile}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
DisableWelcomePage=no
DisableDirPage=no
DisableReadyMemo=no
DisableFinishedPage=no
ShowLanguageDialog=no
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=AI Driver Drowsiness Detection System Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
SetupLogging=yes

; Optional wizard images:
; Put these files in your project folder if you want premium installer look
; installer_side.bmp  = 164 x 314 bmp
; installer_top.bmp   = 55 x 55 bmp
WizardImageFile={#MyProjectDir}\installer_side.bmp
WizardSmallImageFile={#MyProjectDir}\installer_top.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"
Name: "quicklaunchicon"; Description: "Create a Quick Launch shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel1.Caption := 'Welcome to the AI Drowsiness Detection Setup Wizard';
  WizardForm.WelcomeLabel2.Caption :=
    'This installer will guide you through the installation of the AI Driver Drowsiness Detection System.' + #13#10#13#10 +
    'It includes the premium PySide6 interface, integrated camera detection engine, alert workflow, and deployment-ready desktop application.';
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    WizardForm.FinishedLabel.Caption :=
      'AI Drowsiness Detection has been installed successfully.' + #13#10#13#10 +
      'You can launch the application now using the desktop shortcut or Start Menu.';
  end;
end;