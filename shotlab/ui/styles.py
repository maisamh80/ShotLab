APP_STYLESHEET = """
QWidget {
    color: #e5e7e4;
    background: #0a0c0d;
    font-family: "Segoe UI", "Tahoma";
    font-size: 10.5pt;
}
QLabel, QLabel#BrandLogo, QWidget#Transparent {
    background: transparent;
    border: none;
}
QMainWindow, QDialog {
    background: #090b0c;
}
QDialog#ConfirmationDialog, QDialog#DeveloperCreditDialog {
    background: transparent;
}
QDialog#AnnotationBoardDialog {
    background: transparent;
}
QFrame#AnnotationBoard {
    background: #101415;
    border: 1px solid #4d4430;
    border-radius: 16px;
}
QLabel#AnnotationTitle {
    color: #e1bb69;
    font-size: 17pt;
    font-weight: 700;
}
QPushButton#AnnotationClose {
    min-width: 36px;
    max-width: 36px;
    min-height: 34px;
    max-height: 34px;
    padding: 0;
    color: #aeb7b5;
    background: transparent;
    border: 1px solid #303838;
    border-radius: 17px;
    font-size: 18pt;
}
QPushButton#AnnotationTool {
    min-width: 38px;
    min-height: 36px;
    padding: 2px 9px;
    color: #d8b365;
    background: #151a1b;
    border: 1px solid #303838;
    border-radius: 7px;
    font-size: 14pt;
}
QPushButton#AnnotationTool:hover,
QPushButton#AnnotationTool:checked {
    color: #f1c979;
    background: #302817;
    border-color: #e7c87f;
}
QFrame#DeveloperCreditPanel {
    background: #111617;
    border: 1px solid #4d4430;
    border-radius: 16px;
}
QLabel#DeveloperCreditTitle {
    color: #e1bb69;
    font-size: 21pt;
    font-weight: 700;
    letter-spacing: 3px;
}
QFrame#DeveloperCreditAccent {
    background: #d5ae62;
    border: none;
    border-radius: 1px;
}
QLabel#DeveloperCreditMessage {
    color: #d8dcda;
    font-size: 12pt;
}
QLabel#StatusToast {
    color: #f8f4e9;
    background: #202727;
    border: 1px solid #b08d4c;
    border-radius: 9px;
    padding: 9px 16px;
    font-size: 10.5pt;
    font-weight: 600;
}
QFrame#WarningDialog {
    background: #111617;
    border: 1px solid #3a4241;
    border-radius: 16px;
}
QLabel#WarningTitle {
    color: #f2efe7;
    font-size: 18pt;
    font-weight: 650;
}
QLabel#WarningMessage {
    color: #aeb7b5;
    font-size: 11.5pt;
    padding: 0 12px;
}
QPushButton#WarningClose {
    min-height: 0;
    padding: 0;
    color: #8f9997;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 16px;
    font-size: 18pt;
}
QPushButton#WarningClose:hover {
    color: #f2efe7;
    background: #202627;
    border-color: #3b4443;
}
QPushButton#WarningCancel {
    min-height: 40px;
    background: #191f20;
    border-color: #343c3c;
    font-size: 11pt;
}
QPushButton#Destructive {
    min-height: 40px;
    color: #fff3ef;
    background: #a34d45;
    border-color: #be655c;
    font-size: 11pt;
    font-weight: 650;
}
QPushButton#Destructive:hover {
    background: #bd5c52;
    border-color: #d8786e;
}
QFrame#Sidebar, QFrame#Inspector {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #131818,stop:1 #0c0f10);
    border: 1px solid #23292a;
}
QFrame#Sidebar {
    border-right: 1px solid #263130;
}
QFrame#ProjectCard {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #151a1b,stop:1 #101313);
    border: 1px solid #2a3131;
    border-radius: 10px;
}
QFrame#FilterPanel {
    background: #101414;
    border: 1px solid #252d2d;
    border-radius: 8px;
}
QFrame#ProjectCard:hover {
    border-color: #806d45;
    background: #181d1d;
}
QFrame#Mosaic {
    background: #070909;
    border: 1px solid #202727;
    border-radius: 6px;
}
QFrame#LibraryPalette {
    background: #15191a;
    border: 1px solid #2a3131;
    border-radius: 2px;
}
QLabel#MosaicCell {
    color: #8a754a;
    background: #0a0d0e;
    border: none;
    font-size: 22pt;
}
QLabel#CardTitle {
    color: #f0eee7;
    font-size: 12pt;
    font-weight: 600;
}
QFrame#Toolbar, QFrame#Transport {
    background: #0f1213;
    border: 1px solid #202627;
}
QLabel#Brand {
    color: #f1f0ea;
    font-size: 20pt;
    font-weight: 600;
}
QLabel#Eyebrow {
    color: #d5ae62;
    font-size: 8pt;
    font-weight: 700;
}
QLabel#SectionEyebrow {
    color: #d5ae62;
    font-size: 10.5pt;
    font-weight: 700;
    letter-spacing: 1px;
}
QLabel#Title {
    color: #f1f0ed;
    font-size: 18pt;
    font-weight: 500;
}
QLabel#Muted, QLabel#SessionNotice {
    color: #7d8584;
}
QLabel#SidebarSection {
    color: #8f9997;
    font-size: 11.5pt;
    font-weight: 650;
}
QLabel#SidebarFooter {
    color: #697270;
    font-size: 8.5pt;
}
QLabel#MetricValue {
    color: #f0c979;
    font-weight: 600;
}
QFrame#DetailHeading {
    background: #101515;
    border: 1px solid #293130;
    border-radius: 7px;
}
QLabel#DetailTitle {
    color: #f3f1eb;
    font-size: 16.5pt;
    font-weight: 550;
}
QLabel#DetailTime {
    color: #d8b365;
    font-family: "Consolas", "Courier New";
    font-size: 9.5pt;
    font-weight: 650;
}
QLabel#FramePreview {
    background: #050707;
    border: 1px solid #28302f;
    border-radius: 5px;
}
QScrollArea#DetailScroll, QWidget#DetailBody {
    background: transparent;
    border: none;
}
QFrame#GalleryBrowser {
    background: #0c0f10;
    border: 1px solid #222829;
    border-radius: 7px;
}
QFrame#DetailRow, QFrame#DetailNotes {
    background: #0d1111;
    border: 1px solid #252c2c;
    border-radius: 6px;
}
QLabel#DetailKey {
    color: #929b99;
    font-size: 10.5pt;
    font-weight: 600;
}
QLabel#DetailValue {
    color: #f0eee8;
    font-size: 12.5pt;
    font-weight: 500;
}
QLabel#DetailNotesValue {
    color: #d7dcda;
    font-size: 11.5pt;
}
QLabel#DetailEmpty {
    color: #737d7a;
    background: #0d1111;
    border: 1px dashed #303938;
    border-radius: 7px;
    font-size: 11.5pt;
    padding: 18px;
}
QLabel#EmptyState {
    color: #697371;
    background: #0d1011;
    border: 1px dashed #303838;
    border-radius: 10px;
    font-size: 12pt;
}
QPushButton {
    min-height: 34px;
    padding: 0 12px;
    color: #dfe2de;
    background: #181c1d;
    border: 1px solid #2c3233;
    border-radius: 5px;
}
QPushButton:hover {
    background: #202526;
    border-color: #464d4d;
}
QPushButton#Primary, QPushButton#Capture {
    color: #17130d;
    background: #d8b365;
    border-color: #d8b365;
    font-weight: 700;
}
QPushButton#Nav {
    min-height: 50px;
    padding: 0 14px;
    text-align: left;
    color: #aeb7b5;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    font-size: 13.5pt;
    font-weight: 550;
}
QPushButton#Nav:hover {
    color: #f1eee5;
    background: #171d1d;
}
QPushButton#Nav:checked {
    color: #f0c979;
    background: #242116;
    border-color: #4b4129;
}
QPushButton#SidebarAction {
    min-height: 48px;
    padding: 0 14px;
    text-align: left;
    color: #aeb7b5;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    font-size: 13pt;
    font-weight: 550;
}
QPushButton#SidebarAction:hover {
    color: #f1eee5;
    background: #171d1d;
    border-color: #303737;
}
QPushButton#Primary:hover, QPushButton#Capture:hover {
    background: #ebc679;
}
QPushButton#Danger {
    color: #e9a19b;
    background: transparent;
    border-color: #553432;
}
QPushButton#SidebarToggle {
    min-height: 46px;
    padding: 0;
    color: #aeb7b5;
    background: transparent;
    border: 1px solid #303737;
    border-radius: 13px;
    font-size: 14pt;
}
QPushButton#TransportButton {
    min-height: 0;
    padding: 0;
    color: #e5d19d;
    background: #151a1a;
    border: 1px solid #333b3a;
    border-radius: 7px;
    font-size: 14pt;
}
QPushButton#TransportButton:hover {
    color: #fff0c9;
    background: #222827;
    border-color: #806d45;
}
QPushButton#TransportButton:checked {
    background: #2c281a;
    border-color: #9d8149;
}
QPushButton#ThumbnailSize {
    min-height: 0;
    padding: 0;
    background: #151a1a;
    border: 1px solid #333b3a;
    border-radius: 7px;
}
QPushButton#ThumbnailSize:hover {
    background: #242116;
    border-color: #806d45;
}
QPushButton#ThumbnailSize:disabled {
    background: #101313;
    border-color: #242a29;
}
QPushButton#ThumbnailImport {
    min-height: 36px;
    padding: 0 12px;
    color: #e6c77d;
    background: #151a1a;
    border: 1px solid #333b3a;
    border-radius: 7px;
    font-size: 10.5pt;
    font-weight: 650;
}
QPushButton#ThumbnailImport:hover {
    color: #f4d58c;
    background: #242116;
    border-color: #806d45;
}
QPushButton#ProjectAction, QPushButton#ProjectDelete {
    min-height: 0;
    padding: 0;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
}
QPushButton#ProjectAction:hover {
    background: #242116;
    border-color: #66562f;
}
QPushButton#ProjectDelete:hover {
    background: #2d1d1b;
    border-color: #70413c;
}
QPushButton#Quiet {
    color: #aab2b0;
    background: transparent;
}
QLineEdit, QComboBox, QTextEdit {
    min-height: 32px;
    padding: 3px 8px;
    color: #e6e8e5;
    background: #0b0e0f;
    border: 1px solid #2a3031;
    border-radius: 4px;
    selection-background-color: #806938;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border-color: #ad8d50;
}
QLabel#Timecode {
    color: #aeb7b5;
    font-family: "Consolas", "Courier New";
    font-size: 10.5pt;
}
QListWidget {
    background: #0c0f10;
    border: 1px solid #222829;
    border-radius: 6px;
    outline: 0;
}
QListWidget::item {
    min-height: 42px;
    padding: 8px;
    border-bottom: 1px solid #171c1d;
}
QListWidget::item:selected {
    color: #f0d69c;
    background: #252116;
}
QListWidget#ThumbnailList {
    border: none;
    border-radius: 4px;
}
QListWidget#ThumbnailList::item {
    min-height: 0;
    padding: 4px;
    border-bottom: none;
    font-size: 9.5pt;
}
QSlider::groove:horizontal {
    height: 8px;
    background: #343a3a;
    border-radius: 4px;
}
QSlider::sub-page:horizontal {
    background: #b99652;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 24px;
    margin: -11px 0;
    background: transparent;
    border: none;
}
QScrollBar:vertical {
    width: 9px;
    background: #0d1011;
}
QScrollBar::handle:vertical {
    min-height: 24px;
    background: #343a3a;
    border-radius: 4px;
}
QSplitter::handle {
    background: #242a2b;
}
QSplitter#CaptureVerticalSplitter::handle:vertical {
    height: 8px;
    margin: 2px 0;
    background: #313938;
    border-radius: 3px;
}
QSplitter#CaptureVerticalSplitter::handle:vertical:hover {
    background: #9d8149;
}
"""


LIGHT_STYLESHEET = """
QWidget {
    color: #24302f;
    background: #eef1ef;
    font-family: "Segoe UI", "Tahoma";
    font-size: 10.5pt;
}
QLabel, QLabel#BrandLogo, QWidget#Transparent {
    background: transparent;
    border: none;
}
QMainWindow, QDialog { background: #e9eeeb; }
QDialog#ConfirmationDialog, QDialog#DeveloperCreditDialog { background: transparent; }
QFrame#DeveloperCreditPanel {
    background: #f9faf8; border: 1px solid #b79a5c; border-radius: 16px;
}
QLabel#DeveloperCreditTitle {
    color: #856b35; font-size: 21pt; font-weight: 700; letter-spacing: 3px;
}
QFrame#DeveloperCreditAccent {
    background: #a9843e; border: none; border-radius: 1px;
}
QLabel#DeveloperCreditMessage { color: #34413e; font-size: 12pt; }
QLabel#StatusToast {
    color: #26302e; background: #fffdf5; border: 1px solid #a9843e;
    border-radius: 9px; padding: 9px 16px; font-size: 10.5pt; font-weight: 600;
}
QFrame#WarningDialog {
    background: #f9faf8; border: 1px solid #bdc8c3; border-radius: 16px;
}
QLabel#WarningTitle { color: #17211f; font-size: 18pt; font-weight: 650; }
QLabel#WarningMessage { color: #5d6a67; font-size: 11.5pt; padding: 0 12px; }
QPushButton#WarningClose {
    min-height: 0; padding: 0; color: #64716e; background: transparent;
    border: 1px solid transparent; border-radius: 16px; font-size: 18pt;
}
QPushButton#WarningClose:hover {
    color: #17211f; background: #e4e9e6; border-color: #bdc8c3;
}
QPushButton#WarningCancel {
    min-height: 40px; background: #e4e9e6; border-color: #bdc8c3; font-size: 11pt;
}
QPushButton#Destructive {
    min-height: 40px; color: #ffffff; background: #a84e46;
    border-color: #93423c; font-size: 11pt; font-weight: 650;
}
QPushButton#Destructive:hover { background: #bd5c52; border-color: #a44840; }
QFrame#Sidebar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #f9faf7,stop:1 #dde6e1);
    border: 1px solid #c9d3ce;
}
QFrame#Inspector, QFrame#Toolbar, QFrame#Transport {
    background: #f7f9f7;
    border: 1px solid #cbd4d0;
}
QFrame#ProjectCard {
    background: #f9faf8;
    border: 1px solid #c9d2ce;
    border-radius: 10px;
}
QFrame#FilterPanel {
    background: #f7f9f7;
    border: 1px solid #cbd4d0;
    border-radius: 8px;
}
QFrame#ProjectCard:hover { border-color: #9b7d40; background: #ffffff; }
QFrame#Mosaic { background: #dfe5e2; border: 1px solid #c3cdc8; border-radius: 6px; }
QFrame#LibraryPalette {
    background: #e4e9e6; border: 1px solid #c3cdc8; border-radius: 2px;
}
QLabel#MosaicCell { color: #9b7d40; background: #e8ecea; border: none; font-size: 22pt; }
QLabel#Brand { color: #182221; font-size: 20pt; font-weight: 650; }
QLabel#Eyebrow { color: #856b35; font-size: 8pt; font-weight: 700; }
QLabel#SectionEyebrow {
    color: #856b35; font-size: 10.5pt; font-weight: 700; letter-spacing: 1px;
}
QLabel#Title { color: #17211f; font-size: 18pt; font-weight: 550; }
QLabel#CardTitle { color: #1b2624; font-size: 12pt; font-weight: 650; }
QLabel#Muted, QLabel#SessionNotice { color: #64716e; }
QLabel#SidebarSection { color: #5d6a67; font-size: 11.5pt; font-weight: 650; }
QLabel#SidebarFooter { color: #74817d; font-size: 8.5pt; }
QLabel#MetricValue { color: #856b35; font-weight: 700; }
QFrame#DetailHeading {
    background: #eef2ef; border: 1px solid #c6d0cb; border-radius: 7px;
}
QLabel#DetailTitle { color: #17211f; font-size: 16.5pt; font-weight: 600; }
QLabel#DetailTime {
    color: #856b35; font-family: "Consolas", "Courier New";
    font-size: 9.5pt; font-weight: 650;
}
QLabel#FramePreview {
    background: #e2e7e4; border: 1px solid #bdc8c3; border-radius: 5px;
}
QScrollArea#DetailScroll, QWidget#DetailBody { background: transparent; border: none; }
QFrame#GalleryBrowser {
    background: #f7f9f7; border: 1px solid #c6d0cb; border-radius: 7px;
}
QFrame#DetailRow, QFrame#DetailNotes {
    background: #f9faf8; border: 1px solid #d0d8d4; border-radius: 6px;
}
QLabel#DetailKey { color: #64716e; font-size: 10.5pt; font-weight: 650; }
QLabel#DetailValue { color: #1d2927; font-size: 12.5pt; font-weight: 550; }
QLabel#DetailNotesValue { color: #3f4c49; font-size: 11.5pt; }
QLabel#DetailEmpty {
    color: #6f7b77; background: #f4f7f5; border: 1px dashed #b8c4be;
    border-radius: 7px; font-size: 11.5pt; padding: 18px;
}
QLabel#EmptyState {
    color: #6f7b77; background: #f4f7f5; border: 1px dashed #b8c4be;
    border-radius: 10px; font-size: 12pt;
}
QPushButton {
    min-height: 34px;
    padding: 0 12px;
    color: #24302f;
    background: #e4e9e6;
    border: 1px solid #bdc8c3;
    border-radius: 5px;
}
QPushButton:hover { background: #f9fbfa; border-color: #8f9d97; }
QPushButton#Primary, QPushButton#Capture {
    color: #16130d;
    background: #caa75d;
    border-color: #b28f49;
    font-weight: 700;
}
QPushButton#Nav {
    min-height: 50px; padding: 0 14px; text-align: left;
    color: #53615e; background: transparent; border: 1px solid transparent; border-radius: 6px;
    font-size: 13.5pt; font-weight: 550;
}
QPushButton#Nav:hover { color: #182321; background: #e1e8e4; }
QPushButton#Nav:checked { color: #735b2b; background: #f1e8d3; border-color: #d8c59d; }
QPushButton#SidebarAction {
    min-height: 48px; padding: 0 14px; text-align: left;
    color: #53615e; background: transparent; border: 1px solid transparent; border-radius: 6px;
    font-size: 13pt; font-weight: 550;
}
QPushButton#SidebarAction:hover {
    color: #182321; background: #e1e8e4; border-color: #bdc8c3;
}
QPushButton#Danger { color: #a0403a; background: transparent; border-color: #d9aaa6; }
QPushButton#SidebarToggle {
    min-height: 46px; padding: 0; color: #53615e; background: #eef1ef;
    border: 1px solid #bdc8c3; border-radius: 13px; font-size: 14pt;
}
QPushButton#TransportButton {
    min-height: 0; padding: 0; color: #6e572a; background: #eef2ef;
    border: 1px solid #b7c3bd; border-radius: 7px; font-size: 14pt;
}
QPushButton#TransportButton:hover {
    color: #3f3117; background: #ffffff; border-color: #9b7d40;
}
QPushButton#TransportButton:checked {
    background: #f1e5ca; border-color: #a88748;
}
QPushButton#ThumbnailSize {
    min-height: 0; padding: 0; background: #eef2ef;
    border: 1px solid #b7c3bd; border-radius: 7px;
}
QPushButton#ThumbnailSize:hover {
    background: #ffffff; border-color: #9b7d40;
}
QPushButton#ThumbnailSize:disabled {
    background: #e3e8e5; border-color: #ccd4d0;
}
QPushButton#ThumbnailImport {
    min-height: 36px; padding: 0 12px; color: #765d2c;
    background: #eef2ef; border: 1px solid #b7c3bd; border-radius: 7px;
    font-size: 10.5pt; font-weight: 650;
}
QPushButton#ThumbnailImport:hover {
    color: #4d3b1c; background: #ffffff; border-color: #9b7d40;
}
QPushButton#ProjectAction, QPushButton#ProjectDelete {
    min-height: 0; padding: 0; background: transparent;
    border: 1px solid transparent; border-radius: 6px;
}
QPushButton#ProjectAction:hover {
    background: #f1e8d3; border-color: #c5ad79;
}
QPushButton#ProjectDelete:hover {
    background: #f4deda; border-color: #d3a09b;
}
QPushButton#Quiet { color: #64716e; background: transparent; }
QLineEdit, QComboBox, QTextEdit {
    min-height: 32px; padding: 3px 8px; color: #1c2826; background: #ffffff;
    border: 1px solid #bdc9c4; border-radius: 4px; selection-background-color: #d6bd82;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border-color: #94753a; }
QLabel#Timecode {
    color: #53615e; font-family: "Consolas", "Courier New"; font-size: 10.5pt;
}
QListWidget { background: #f7f9f7; border: 1px solid #c6d0cb; border-radius: 6px; outline: 0; }
QListWidget::item { min-height: 42px; padding: 8px; border-bottom: 1px solid #e0e6e3; }
QListWidget::item:selected { color: #5f4a22; background: #f1e5ca; }
QListWidget#ThumbnailList { border: none; border-radius: 4px; }
QListWidget#ThumbnailList::item {
    min-height: 0; padding: 4px; border-bottom: none; font-size: 9.5pt;
}
QSlider::groove:horizontal { height: 8px; background: #bac5c0; border-radius: 4px; }
QSlider::sub-page:horizontal { background: #a88748; border-radius: 4px; }
QSlider::handle:horizontal {
    width: 24px; margin: -11px 0; background: transparent; border: none;
}
QScrollBar:vertical { width: 9px; background: #e2e8e5; }
QScrollBar::handle:vertical { min-height: 24px; background: #aab6b1; border-radius: 4px; }
QSplitter::handle { background: #c8d1cd; }
QSplitter#CaptureVerticalSplitter::handle:vertical {
    height: 8px; margin: 2px 0; background: #aebbb5; border-radius: 3px;
}
QSplitter#CaptureVerticalSplitter::handle:vertical:hover { background: #a88748; }
"""

FINAL_DARK_OVERRIDES = """
QWidget {
    color: #E8E8E3;
    background: #090C0C;
    font-family: "Inter", "Vazirmatn";
    font-size: 9.5pt;
}
QMainWindow, QDialog { background: #090C0C; }
QFrame#Sidebar {
    background: #101616;
    border: none;
    border-right: 1px solid #29302F;
}
QLabel#BrandLogo, QLabel, QWidget#Transparent {
    background: transparent;
}
QLabel#SidebarSection {
    color: #8B918F;
    font-size: 8.5pt;
    font-weight: 500;
    padding: 5px 5px 2px 5px;
}
QLabel#SidebarFooter {
    color: #8A908E;
    font-size: 7.5pt;
}
QPushButton#Nav, QPushButton#SidebarAction {
    min-height: 39px;
    padding: 0 10px;
    color: #B9BFBC;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 10pt;
    font-weight: 420;
}
QPushButton#Nav:hover, QPushButton#SidebarAction:hover {
    color: #FFFFFF;
    background: #192120;
    border-color: transparent;
}
QPushButton#Nav:checked {
    color: #D8B365;
    background: #2B2517;
    border-color: #66562F;
}
QPushButton#RoundControl {
    min-height: 0;
    max-width: 38px;
    padding: 0;
    color: #D8B365;
    background: #29230F;
    border: 1px solid #3D341B;
    border-radius: 19px;
    font-size: 9pt;
    font-weight: 600;
}
QPushButton#RoundControl:hover {
    color: #F4D181;
    background: #3A3117;
    border-color: #7A6634;
}
QMenu {
    color: #E8E8E3;
    background: #18201F;
    border: 1px solid #48504E;
    padding: 5px;
}
QMenu::item { padding: 7px 22px; border-radius: 3px; }
QMenu::item:selected { color: #17130D; background: #D8B365; }
QPushButton#SidebarToggle {
    min-height: 40px;
    background: #101616;
    border: 1px solid #303837;
    border-radius: 11px;
}
QLabel#Title {
    color: #D8B365;
    font-size: 12pt;
    font-weight: 520;
}
QLabel#SectionEyebrow {
    color: #D8B365;
    font-size: 8pt;
    letter-spacing: 0;
}
QFrame#FilterPanel {
    background: #101616;
    border: 1px solid #303736;
    border-radius: 4px;
}
QLineEdit, QComboBox, QTextEdit {
    min-height: 28px;
    padding: 2px 7px;
    color: #E8E8E3;
    background: #0B0F0F;
    border: 1px solid #303736;
    border-radius: 3px;
    selection-background-color: #816B38;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border-color: #D8B365;
}
QPushButton {
    min-height: 30px;
    padding: 0 10px;
    border-radius: 3px;
    font-size: 9pt;
}
QPushButton#Primary, QPushButton#Capture {
    color: #17130D;
    background: #D8B365;
    border: 1px solid #D8B365;
}
QPushButton#Primary:hover, QPushButton#Capture:hover {
    background: #E9C475;
    border-color: #E9C475;
}
QFrame#ProjectCard {
    background: #101616;
    border: 1px solid #303736;
    border-radius: 4px;
}
QFrame#ProjectCard:hover {
    background: #131A19;
    border-color: #D8B365;
}
QFrame#Mosaic {
    background: #080B0B;
    border: 1px solid #303736;
    border-radius: 2px;
}
QLabel#MosaicCell { background: #080B0B; }
QLabel#CardTitle {
    color: #E8E8E3;
    font-size: 9.5pt;
    font-weight: 520;
}
QFrame#Inspector, QFrame#GalleryBrowser, QFrame#Transport {
    background: #101616;
    border: 1px solid #303736;
    border-radius: 3px;
}
QFrame#DetailHeading, QFrame#DetailRow, QFrame#DetailNotes {
    background: #0C1111;
    border: 1px solid #29302F;
    border-radius: 3px;
}
QLabel#DetailTitle { font-size: 12pt; }
QLabel#DetailKey { font-size: 8.5pt; }
QLabel#DetailValue { font-size: 9.5pt; }
QListWidget, QListWidget#ThumbnailList {
    background: #090D0D;
    border: 1px solid #29302F;
    border-radius: 2px;
}
QListWidget#ThumbnailList::item {
    padding: 3px;
    border: none;
    font-size: 8pt;
}
QListWidget#ThumbnailList::item:selected {
    color: #F1D28C;
    background: #2B2517;
    border: 1px solid #6A5830;
}
QPushButton#TransportButton, QPushButton#ThumbnailSize {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
}
QPushButton#TransportButton:hover, QPushButton#ThumbnailSize:hover {
    background: #202827;
    border-color: #66562F;
}
QPushButton#ThumbnailImport {
    color: #D8B365;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
}
QPushButton#ThumbnailImport:hover {
    background: #202827;
    border-color: #66562F;
}
QSlider::groove:horizontal {
    height: 5px;
    background: #40504E;
    border-radius: 1px;
}
QSlider::sub-page:horizontal {
    background: #D8B365;
    border-radius: 1px;
}
QLabel#Timecode {
    color: #939A97;
    font-family: "Inter";
    font-size: 8pt;
}
QDialog#PdfExportDialog {
    background: #101616;
    border: 1px solid #6D5C34;
}
QLabel#PdfDialogTitle {
    color: #F0F0EB;
    font-size: 17pt;
    font-weight: 430;
}
QRadioButton { color: #999F9C; spacing: 7px; }
QRadioButton::indicator {
    width: 15px; height: 15px;
    border: 1px solid #CED2D0; border-radius: 8px;
}
QRadioButton::indicator:checked {
    background: #D8B365;
    border: 3px solid #101616;
}
"""

FINAL_LIGHT_OVERRIDES = """
QWidget {
    color: #232323;
    background: #ECEDEC;
    font-family: "Inter", "Vazirmatn";
    font-size: 9.5pt;
}
QMainWindow, QDialog { background: #ECEDEC; }
QFrame#Sidebar {
    background: #F7F7F2;
    border: none;
    border-right: 1px solid #CFD3D0;
}
QLabel#BrandLogo, QLabel, QWidget#Transparent {
    background: transparent;
}
QLabel#SidebarSection {
    color: #858A87;
    font-size: 8.5pt;
    font-weight: 500;
    padding: 5px 5px 2px 5px;
}
QLabel#SidebarFooter { color: #858A87; font-size: 7.5pt; }
QPushButton#Nav, QPushButton#SidebarAction {
    min-height: 39px;
    padding: 0 10px;
    color: #737976;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 10pt;
    font-weight: 420;
}
QPushButton#Nav:hover, QPushButton#SidebarAction:hover {
    color: #232323;
    background: #E2E9E5;
}
QPushButton#Nav:checked {
    color: #9B7424;
    background: #F5EBD5;
    border-color: #E5C982;
}
QPushButton#RoundControl {
    min-height: 0;
    max-width: 38px;
    padding: 0;
    color: #A77C28;
    background: #F5EBD5;
    border: 1px solid #E7D5AE;
    border-radius: 19px;
    font-size: 9pt;
    font-weight: 600;
}
QPushButton#RoundControl:hover {
    background: #FFF8E8;
    border-color: #D8B365;
}
QMenu {
    color: #232323;
    background: #FAFBF9;
    border: 1px solid #C9CFCC;
    padding: 5px;
}
QMenu::item { padding: 7px 22px; border-radius: 3px; }
QMenu::item:selected { color: #17130D; background: #D8B365; }
QPushButton#SidebarToggle {
    min-height: 40px;
    background: #F7F7F2;
    border: 1px solid #CED3D0;
    border-radius: 11px;
}
QLabel#Title {
    color: #A77C28;
    font-size: 12pt;
    font-weight: 520;
}
QLabel#SectionEyebrow {
    color: #A77C28;
    font-size: 8pt;
    letter-spacing: 0;
}
QFrame#FilterPanel {
    background: #F7F8F6;
    border: 1px solid #CCD2CF;
    border-radius: 4px;
}
QLineEdit, QComboBox, QTextEdit {
    min-height: 28px;
    padding: 2px 7px;
    color: #232323;
    background: #FFFFFF;
    border: 1px solid #CDD3D0;
    border-radius: 3px;
    selection-background-color: #E8D19A;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border-color: #B28835;
}
QPushButton {
    min-height: 30px;
    padding: 0 10px;
    border-radius: 3px;
    font-size: 9pt;
}
QPushButton#Primary, QPushButton#Capture {
    color: #17130D;
    background: #D8B365;
    border: 1px solid #CAA552;
}
QPushButton#Primary:hover, QPushButton#Capture:hover {
    background: #E5C376;
}
QFrame#ProjectCard {
    background: #FBFCFA;
    border: 1px solid #CCD2CF;
    border-radius: 4px;
}
QFrame#ProjectCard:hover {
    background: #FFFFFF;
    border-color: #B48B39;
}
QFrame#Mosaic {
    background: #E5E8E6;
    border: 1px solid #CCD2CF;
    border-radius: 2px;
}
QLabel#MosaicCell { background: #E8EBE9; }
QLabel#CardTitle {
    color: #232323;
    font-size: 9.5pt;
    font-weight: 520;
}
QFrame#Inspector, QFrame#GalleryBrowser, QFrame#Transport {
    background: #F8F9F7;
    border: 1px solid #CCD2CF;
    border-radius: 3px;
}
QFrame#DetailHeading, QFrame#DetailRow, QFrame#DetailNotes {
    background: #FFFFFF;
    border: 1px solid #D5DAD7;
    border-radius: 3px;
}
QLabel#DetailTitle { font-size: 12pt; }
QLabel#DetailKey { font-size: 8.5pt; }
QLabel#DetailValue { font-size: 9.5pt; }
QListWidget, QListWidget#ThumbnailList {
    background: #F8F9F7;
    border: 1px solid #CCD2CF;
    border-radius: 2px;
}
QListWidget#ThumbnailList::item {
    padding: 3px;
    border: none;
    font-size: 8pt;
}
QListWidget#ThumbnailList::item:selected {
    color: #684D1D;
    background: #F5EBD5;
    border: 1px solid #D8B365;
}
QPushButton#TransportButton, QPushButton#ThumbnailSize {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
}
QPushButton#TransportButton:hover, QPushButton#ThumbnailSize:hover {
    background: #E2E9E5;
    border-color: #D1B36D;
}
QPushButton#ThumbnailImport {
    color: #A77C28;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
}
QPushButton#ThumbnailImport:hover {
    background: #F5EBD5;
    border-color: #D8B365;
}
QSlider::groove:horizontal {
    height: 5px;
    background: #B9C5C0;
    border-radius: 1px;
}
QSlider::sub-page:horizontal {
    background: #D8B365;
    border-radius: 1px;
}
QLabel#Timecode {
    color: #858A87;
    font-family: "Inter";
    font-size: 8pt;
}
QDialog#PdfExportDialog {
    background: #FBFCFA;
    border: 1px solid #D8B365;
}
QLabel#PdfDialogTitle {
    color: #232323;
    font-size: 17pt;
    font-weight: 430;
}
QRadioButton { color: #858A87; spacing: 7px; }
QRadioButton::indicator {
    width: 15px; height: 15px;
    border: 1px solid #858A87; border-radius: 8px;
}
QRadioButton::indicator:checked {
    background: #D8B365;
    border: 3px solid #FBFCFA;
}
"""

REFERENCE_DARK_STYLESHEET = """
QWidget {
    color: #E6E7E4;
    background: transparent;
    font-family: "Inter", "Vazirmatn";
    font-size: 10.5pt;
}
QMainWindow, QWidget#CentralShell, QWidget#LibraryPage,
QWidget#CapturePage, QWidget#GalleryPage, QDialog {
    background: #080C0C;
}
QLabel { background: transparent; border: none; }
QFrame#Sidebar {
    background: #101616;
    border: none;
    border-right: 1px solid #52605E;
}
QLabel#BrandLogo { background: transparent; }
QLabel#SidebarSection {
    color: #8E9290;
    font-size: 11pt;
    font-weight: 500;
    padding: 0 8px;
}
QLabel#SidebarFooter {
    color: #555B59;
    font-size: 9.5pt;
}
QPushButton#Nav, QPushButton#SidebarAction {
    min-height: 52px;
    padding: 0 12px;
    color: #8D918F;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 12.5pt;
    font-weight: 500;
}
QPushButton#Nav:hover, QPushButton#SidebarAction:hover {
    color: #E8E9E6;
    background: #192120;
}
QPushButton#Nav:checked, QPushButton#SidebarAction:pressed {
    color: #DDB75F;
    background: #2B2517;
    border-color: #866C31;
}
QPushButton#Nav:disabled { color: #505654; }
QPushButton#SidebarToggle {
    min-height: 0;
    padding: 0;
    color: #9DA29F;
    background: #101616;
    border: 1px solid #64706E;
    border-radius: 5px;
    font-size: 13pt;
}
QPushButton#RoundControl {
    min-height: 0;
    max-width: 44px;
    padding: 0;
    color: #DDB75F;
    background: #29230F;
    border: none;
    border-radius: 22px;
    font-size: 12pt;
    font-weight: 600;
}
QPushButton#RoundControl:hover { background: #3A3117; }
QLabel#Title {
    color: #DDB75F;
    font-size: 18pt;
    font-weight: 550;
}
QLabel#NeutralSectionTitle {
    color: #F2F2EF;
    font-size: 18pt;
    font-weight: 550;
}
QLabel#WorkspaceProjectTitle {
    color: #AEB2B0;
    font-size: 18pt;
    font-weight: 550;
}
QLabel#ToolbarCaption {
    color: #8D918F;
    font-size: 10.5pt;
    font-weight: 450;
}
QLabel#SectionEyebrow { color: #DDB75F; }
QLabel#SessionNotice {
    color: #B5B8B6;
    font-size: 10.5pt;
}
QPushButton {
    min-height: 36px;
    padding: 0 14px;
    color: #A8ADAA;
    background: #192120;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 10.5pt;
    font-weight: 500;
}
QPushButton:hover {
    color: #E7E8E5;
    background: #222C2A;
}
QPushButton:disabled {
    color: #555C59;
    background: #151B1A;
}
QPushButton#Primary, QPushButton#Capture {
    color: #111513;
    background: #DDB75F;
    border: 1px solid #DDB75F;
    font-weight: 600;
}
QPushButton#Primary:hover, QPushButton#Capture:hover {
    background: #EBC66E;
}
QPushButton#Primary:disabled, QPushButton#Capture:disabled {
    color: #555C59;
    background: #151B1A;
    border-color: #151B1A;
}
QPushButton#Danger, QPushButton#WarningCancel {
    color: #B0B4B2;
    background: #536366;
    border: none;
}
QPushButton#Destructive {
    color: #FFFFFF;
    background: #A7554D;
    border: none;
}
QFrame#FilterPanel {
    background: #121818;
    border: 1px solid #4C5B5B;
    border-radius: 10px;
}
QLabel#FilterLabel {
    color: #8D918F;
    font-size: 10.5pt;
    padding-left: 8px;
    padding-right: 8px;
}
QLabel#FormLabel {
    color: #8D918F;
    font-size: 10pt;
}
QLineEdit, QComboBox, QTextEdit {
    min-height: 36px;
    padding: 0 10px;
    color: #A7ABA9;
    background: #050909;
    border: 1px solid #111717;
    border-radius: 4px;
    selection-background-color: #8A713A;
}
QTextEdit { padding: 7px 10px; }
QLineEdit#Search {
    min-height: 38px;
    border: 1px solid #0C1111;
    font-size: 10.5pt;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    color: #E6E7E4;
    border-color: #7D6837;
}
QComboBox::drop-down {
    width: 28px;
    border: none;
}
QComboBox QAbstractItemView {
    color: #A7ABA9;
    background: #080C0C;
    border: 1px solid #43504E;
    selection-color: #E9EAE7;
    selection-background-color: #2C3534;
    outline: 0;
}
QPushButton#FilterAction {
    min-height: 36px;
    padding: 0 12px;
    color: #939896;
    background: #0C1111;
    border: 1px solid #111717;
    font-weight: 450;
}
QPushButton#FilterAction:hover {
    color: #DDB75F;
    background: #192120;
}
QFrame#ProjectCard {
    background: #121818;
    border: 1px solid #4C5B5B;
    border-radius: 10px;
}
QFrame#ProjectCard:hover { border-color: #DDB75F; }
QFrame#Mosaic {
    background: transparent;
    border: none;
}
QLabel#MosaicCell {
    color: #DDB75F;
    background: #030606;
    border: none;
    border-radius: 4px;
}
QFrame#LibraryPalette {
    background: #0A0D0D;
    border: none;
    border-radius: 4px;
}
QLabel#CardTitle {
    color: #F2F2EF;
    font-size: 11.5pt;
    font-weight: 500;
}
QLabel#CardCount {
    color: #8B8F8D;
    font-size: 9.5pt;
    font-weight: 550;
}
QPushButton#CardMenu {
    min-height: 0;
    padding: 0;
    color: #A7ACAA;
    background: transparent;
    border: none;
    font-size: 20pt;
}
QPushButton#CardMenu:hover { color: #DDB75F; }
QMenu {
    color: #D7D9D6;
    background: #192120;
    border: 1px solid #5C674F;
    padding: 6px;
}
QMenu::item {
    min-width: 170px;
    padding: 8px 22px;
    border-radius: 3px;
}
QMenu::item:selected {
    color: #111513;
    background: #DDB75F;
}
QMenu::separator {
    height: 1px;
    background: #3D4745;
    margin: 4px 8px;
}
QFrame#Inspector, QFrame#GalleryBrowser, QFrame#Transport {
    background: #121818;
    border: 1px solid #4C5B5B;
    border-radius: 10px;
}
QFrame#Inspector { border-radius: 9px; }
QLabel#InspectorTitle, QLabel#DetailTitle {
    color: #D3D5D2;
    font-size: 12pt;
    font-weight: 550;
}
QLabel#InspectorTime, QLabel#DetailTime, QLabel#Timecode {
    color: #858A88;
    font-family: "Inter";
    font-size: 9pt;
}
QWidget#VideoStage, QVideoWidget#VideoWidget {
    background: #050909;
    border: none;
}
QLabel#VideoEmpty {
    color: #888D8B;
    background: transparent;
    padding: 30px;
    font-size: 11.5pt;
}
QLabel#FramePreview {
    background: #050909;
    border: none;
    border-radius: 4px;
}
QFrame#DetailPalette { border: none; border-radius: 5px; }
QScrollArea, QScrollArea#DetailScroll, QWidget#DetailBody {
    background: transparent;
    border: none;
}
QFrame#DetailRow, QFrame#DetailNotes {
    background: #050909;
    border: none;
    border-radius: 4px;
}
QLabel#DetailKey {
    color: #8D918F;
    font-size: 9.5pt;
}
QLabel#DetailValue {
    color: #CFD1CE;
    font-size: 10pt;
}
QLabel#DetailValueBox {
    color: #A7ABA9;
    background: #050909;
    border: none;
    border-radius: 4px;
    padding: 0 10px;
    font-size: 10pt;
}
QLabel#DetailNotesValue { color: #CFD1CE; font-size: 10pt; }
QLabel#DetailEmpty {
    color: #777D7A;
    background: #050909;
    border: none;
    border-radius: 4px;
    padding: 16px;
}
QListWidget, QListWidget#ThumbnailList {
    color: #8D918F;
    background: transparent;
    border: none;
    outline: 0;
}
QListWidget#ThumbnailList::item {
    padding: 3px;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 9.5pt;
}
QListWidget#ThumbnailList::item:selected {
    color: #DDB75F;
    background: #2B2517;
    border-color: #806A36;
}
QPushButton#TransportButton {
    min-height: 0;
    padding: 0;
    background: transparent;
    border: none;
    border-radius: 4px;
}
QPushButton#TransportButton:hover {
    background: transparent;
}
QPushButton#ThumbnailSize {
    min-height: 0;
    padding: 0;
    background: #192120;
    border: none;
    border-radius: 4px;
}
QPushButton#ThumbnailSize:hover {
    background: #26302E;
}
QPushButton#ThumbnailImport {
    color: #BFC2C0;
    background: #192120;
    border: none;
}
QSplitter#WorkspaceSplitter::handle,
QSplitter#CaptureVerticalSplitter::handle {
    background: transparent;
}
QSplitter#WorkspaceSplitter::handle:hover,
QSplitter#CaptureVerticalSplitter::handle:hover {
    background: #4C5B5B;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #586766;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #A7832D;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 26px;
    margin: -11px 0;
    background: transparent;
    border: none;
}
QScrollBar:vertical {
    width: 8px;
    margin: 0;
    background: transparent;
}
QScrollBar::handle:vertical {
    min-height: 36px;
    background: #5D6D6B;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QToolTip {
    color: #E7E8E5;
    background: #192120;
    border: 1px solid #6F6544;
    padding: 5px;
}
QDialog#ConfirmationDialog, QDialog#DeveloperCreditDialog {
    background: transparent;
}
QDialog#LibraryNameDialog, QDialog#ValidationDialog,
QDialog#ColorPickerDialog, QDialog#PdfExportDialog {
    background: transparent;
    border: none;
}
QFrame#WarningDialog, QFrame#DeveloperCreditPanel {
    background: #1B2524;
    border: 1px solid #8C7136;
    border-radius: 10px;
}
QFrame#DialogPanel, QFrame#ColorPickerPanel,
QFrame#PdfDialogPanel {
    background: #1B2524;
    border: 1px solid #8C7136;
    border-radius: 10px;
}
QLabel#DialogTitle {
    color: #F0F1EE;
    font-size: 16pt;
    font-weight: 450;
}
QLabel#WarningTitle, QLabel#DeveloperCreditTitle {
    color: #F0F1EE;
    font-size: 16pt;
    font-weight: 500;
}
QLabel#WarningMessage, QLabel#DeveloperCreditMessage {
    color: #9B9F9D;
    font-size: 10.5pt;
}
QLabel#ValidationMessage {
    color: #D0D2D0;
    font-size: 11.5pt;
}
QLabel#ColorPickerTitle {
    color: #A9ADAB;
    font-size: 13pt;
    font-weight: 450;
}
QLabel#PdfDialogTitle {
    color: #F0F1EE;
    font-size: 17pt;
    font-weight: 450;
}
QRadioButton { color: #999E9B; spacing: 8px; }
QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #D6D9D6;
    border-radius: 7px;
}
QRadioButton::indicator:checked {
    background: #D6D9D6;
    border: 4px solid #1B2524;
}
QPushButton#TransportButton,
QPushButton#TransportButton:hover,
QPushButton#TransportButton:pressed,
QPushButton#TransportButton:checked,
QPushButton#TransportButton:checked:hover {
    background: transparent;
    border: none;
}
QSplitter#CaptureVerticalSplitter::handle:vertical {
    background: transparent;
    border: none;
}
QSplitter#CaptureVerticalSplitter::handle:vertical:hover {
    background: #4C5B5B;
    border: none;
}
"""

REFERENCE_LIGHT_STYLESHEET = """
QWidget {
    color: #303332;
    background: transparent;
    font-family: "Inter", "Vazirmatn";
    font-size: 10.5pt;
}
QMainWindow, QWidget#CentralShell, QWidget#LibraryPage,
QWidget#CapturePage, QWidget#GalleryPage, QDialog {
    background: #E9EAEA;
}
QLabel { background: transparent; border: none; }
QFrame#Sidebar {
    background: #F5F6F2;
    border: none;
    border-right: 1px solid #A9AEAB;
}
QLabel#SidebarSection {
    color: #868A88;
    font-size: 11pt;
    font-weight: 500;
    padding: 0 8px;
}
QLabel#SidebarFooter { color: #777C79; font-size: 9.5pt; }
QPushButton#Nav, QPushButton#SidebarAction {
    min-height: 52px;
    padding: 0 12px;
    color: #858987;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 12.5pt;
    font-weight: 500;
}
QPushButton#Nav:hover, QPushButton#SidebarAction:hover {
    color: #292C2B;
    background: #E0E8E4;
}
QPushButton#Nav:checked, QPushButton#SidebarAction:pressed {
    color: #A77B20;
    background: #F5EBD4;
    border-color: #E1BD6B;
}
QPushButton#Nav:disabled { color: #B8BCBA; }
QPushButton#SidebarToggle {
    min-height: 0;
    padding: 0;
    color: #8B908D;
    background: #F5F6F2;
    border: 1px solid #AEB3B0;
    border-radius: 5px;
    font-size: 13pt;
}
QPushButton#RoundControl {
    min-height: 0;
    max-width: 44px;
    padding: 0;
    color: #A77B20;
    background: #FFF3D8;
    border: none;
    border-radius: 22px;
    font-size: 12pt;
    font-weight: 600;
}
QPushButton#RoundControl:hover { background: #FFEAB9; }
QLabel#Title {
    color: #A77B20;
    font-size: 18pt;
    font-weight: 550;
}
QLabel#NeutralSectionTitle {
    color: #303332;
    font-size: 18pt;
    font-weight: 550;
}
QLabel#WorkspaceProjectTitle {
    color: #777C79;
    font-size: 18pt;
    font-weight: 550;
}
QLabel#ToolbarCaption {
    color: #777C79;
    font-size: 10.5pt;
    font-weight: 450;
}
QLabel#SessionNotice { color: #555A58; font-size: 10.5pt; }
QPushButton {
    min-height: 36px;
    padding: 0 14px;
    color: #777C79;
    background: #E2E8E5;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 10.5pt;
    font-weight: 500;
}
QPushButton:hover { color: #292C2B; background: #D6DFDB; }
QPushButton:disabled { color: #AEB3B0; background: #E2E7E4; }
QPushButton#Primary, QPushButton#Capture {
    color: #171A19;
    background: #DDB75F;
    border: 1px solid #DDB75F;
    font-weight: 600;
}
QPushButton#Primary:hover, QPushButton#Capture:hover { background: #E7C574; }
QPushButton#Primary:disabled, QPushButton#Capture:disabled {
    color: #AEB3B0;
    background: #E2E7E4;
    border-color: #E2E7E4;
}
QPushButton#Danger, QPushButton#WarningCancel {
    color: #858987;
    background: #E1E7E4;
    border: none;
}
QPushButton#Destructive { color: #FFFFFF; background: #B85D54; border: none; }
QFrame#FilterPanel {
    background: #F7F8F6;
    border: 1px solid #C4CAC7;
    border-radius: 10px;
}
QLabel#FilterLabel {
    color: #777C79;
    font-size: 10.5pt;
    padding-left: 8px;
    padding-right: 8px;
}
QLabel#FormLabel {
    color: #777C79;
    font-size: 10pt;
}
QLineEdit, QComboBox, QTextEdit {
    min-height: 36px;
    padding: 0 10px;
    color: #777C79;
    background: #FFFFFF;
    border: 1px solid #C8CDCA;
    border-radius: 4px;
    selection-background-color: #E5C57D;
}
QTextEdit { padding: 7px 10px; }
QLineEdit#Search { min-height: 38px; font-size: 10.5pt; }
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border-color: #C29A44; }
QComboBox::drop-down { width: 28px; border: none; }
QComboBox QAbstractItemView {
    color: #555A58;
    background: #FFFFFF;
    border: 1px solid #BFC5C2;
    selection-color: #292C2B;
    selection-background-color: #E0E8E4;
    outline: 0;
}
QPushButton#FilterAction {
    min-height: 36px;
    padding: 0 12px;
    color: #777C79;
    background: #FFFFFF;
    border: 1px solid #C8CDCA;
    font-weight: 450;
}
QPushButton#FilterAction:hover { color: #A77B20; background: #F5EBD4; }
QFrame#ProjectCard {
    background: #F9FAF8;
    border: 1px solid #C3C9C6;
    border-radius: 10px;
}
QFrame#ProjectCard:hover { border-color: #DDB75F; }
QFrame#Mosaic { background: transparent; border: none; }
QLabel#MosaicCell {
    color: #A77B20;
    background: #050707;
    border: none;
    border-radius: 4px;
}
QFrame#LibraryPalette { border: none; border-radius: 4px; }
QLabel#CardTitle { color: #202322; font-size: 11.5pt; font-weight: 500; }
QLabel#CardCount { color: #858A87; font-size: 9.5pt; font-weight: 550; }
QPushButton#CardMenu {
    min-height: 0;
    padding: 0;
    color: #A1A6A3;
    background: transparent;
    border: none;
    font-size: 20pt;
}
QPushButton#CardMenu:hover { color: #A77B20; }
QMenu {
    color: #444846;
    background: #FFFFFF;
    border: 1px solid #C3C9C6;
    padding: 6px;
}
QMenu::item { min-width: 170px; padding: 8px 22px; border-radius: 3px; }
QMenu::item:selected { color: #171A19; background: #DDB75F; }
QMenu::separator { height: 1px; background: #D8DDDA; margin: 4px 8px; }
QFrame#Inspector, QFrame#GalleryBrowser, QFrame#Transport {
    background: #F7F8F6;
    border: 1px solid #BFC6C3;
    border-radius: 10px;
}
QLabel#InspectorTitle, QLabel#DetailTitle {
    color: #3A3E3C;
    font-size: 12pt;
    font-weight: 550;
}
QLabel#InspectorTime, QLabel#DetailTime, QLabel#Timecode {
    color: #858A87;
    font-family: "Inter";
    font-size: 9pt;
}
QWidget#VideoStage, QVideoWidget#VideoWidget { background: #050909; border: none; }
QLabel#VideoEmpty {
    color: #858A87;
    background: transparent;
    padding: 30px;
    font-size: 11.5pt;
}
QLabel#FramePreview { background: #050909; border: none; border-radius: 4px; }
QScrollArea, QScrollArea#DetailScroll, QWidget#DetailBody {
    background: transparent;
    border: none;
}
QFrame#DetailRow, QFrame#DetailNotes {
    background: #FFFFFF;
    border: 1px solid #D3D7D5;
    border-radius: 4px;
}
QLabel#DetailKey { color: #777C79; font-size: 9.5pt; }
QLabel#DetailValue { color: #353937; font-size: 10pt; }
QLabel#DetailValueBox {
    color: #555A58;
    background: #FFFFFF;
    border: 1px solid #D3D7D5;
    border-radius: 4px;
    padding: 0 10px;
    font-size: 10pt;
}
QLabel#DetailNotesValue { color: #353937; font-size: 10pt; }
QLabel#DetailEmpty {
    color: #858A87;
    background: #FFFFFF;
    border: 1px solid #D3D7D5;
    border-radius: 4px;
    padding: 16px;
}
QListWidget, QListWidget#ThumbnailList {
    color: #777C79;
    background: transparent;
    border: none;
    outline: 0;
}
QListWidget#ThumbnailList::item {
    padding: 3px;
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 9.5pt;
}
QListWidget#ThumbnailList::item:selected {
    color: #A77B20;
    background: #F5EBD4;
    border-color: #DDB75F;
}
QPushButton#TransportButton {
    min-height: 0;
    padding: 0;
    background: transparent;
    border: none;
    border-radius: 4px;
}
QPushButton#TransportButton:hover {
    background: transparent;
}
QPushButton#ThumbnailSize {
    min-height: 0;
    padding: 0;
    background: #FFFFFF;
    border: 1px solid #D0D5D2;
    border-radius: 4px;
}
QPushButton#ThumbnailSize:hover {
    background: #F5EBD4;
}
QPushButton#ThumbnailImport {
    color: #555A58;
    background: #FFFFFF;
    border: 1px solid #D0D5D2;
}
QSplitter#WorkspaceSplitter::handle,
QSplitter#CaptureVerticalSplitter::handle { background: transparent; }
QSplitter#WorkspaceSplitter::handle:hover,
QSplitter#CaptureVerticalSplitter::handle:hover { background: #BFC6C3; }
QSlider::groove:horizontal { height: 6px; background: #BCC5C1; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #A7832D; border-radius: 3px; }
QSlider::handle:horizontal {
    width: 26px;
    margin: -11px 0;
    background: transparent;
    border: none;
}
QScrollBar:vertical { width: 8px; margin: 0; background: transparent; }
QScrollBar::handle:vertical {
    min-height: 36px;
    background: #9EA9A4;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QToolTip {
    color: #303332;
    background: #FFFFFF;
    border: 1px solid #C3C9C6;
    padding: 5px;
}
QDialog#ConfirmationDialog, QDialog#DeveloperCreditDialog,
QDialog#LibraryNameDialog, QDialog#ValidationDialog,
QDialog#ColorPickerDialog, QDialog#PdfExportDialog {
    background: transparent;
    border: none;
}
QDialog#AnnotationBoardDialog {
    background: transparent;
    border: none;
}
QFrame#AnnotationBoard {
    background: #FFFFFF;
    border: 1px solid #DDB75F;
    border-radius: 10px;
}
QLabel#AnnotationTitle {
    color: #303332;
    font-size: 17pt;
    font-weight: 500;
}
QPushButton#AnnotationTool {
    min-width: 38px;
    min-height: 36px;
    padding: 2px 9px;
    background: #F4F6F5;
    border: 1px solid #C3CBC7;
    border-radius: 7px;
}
QPushButton#AnnotationTool:hover,
QPushButton#AnnotationTool:checked {
    background: #F6EACD;
    border-color: #DDB75F;
}
QFrame#WarningDialog, QFrame#DeveloperCreditPanel {
    background: #FFFFFF;
    border: 1px solid #DDB75F;
    border-radius: 10px;
}
QFrame#DialogPanel, QFrame#ColorPickerPanel,
QFrame#PdfDialogPanel {
    background: #FFFFFF;
    border: 1px solid #DDB75F;
    border-radius: 10px;
}
QLabel#DialogTitle {
    color: #303332;
    font-size: 16pt;
    font-weight: 450;
}
QLabel#WarningTitle, QLabel#DeveloperCreditTitle {
    color: #303332;
    font-size: 16pt;
    font-weight: 500;
}
QLabel#WarningMessage, QLabel#DeveloperCreditMessage {
    color: #858A87;
    font-size: 10.5pt;
}
QLabel#ValidationMessage {
    color: #555A58;
    font-size: 11.5pt;
}
QLabel#ColorPickerTitle {
    color: #777C79;
    font-size: 13pt;
    font-weight: 450;
}
QLabel#PdfDialogTitle { color: #303332; font-size: 17pt; font-weight: 450; }
QRadioButton { color: #858A87; spacing: 8px; }
QRadioButton::indicator {
    width: 14px; height: 14px;
    border: 1px solid #858A87; border-radius: 7px;
}
QRadioButton::indicator:checked {
    background: #858A87;
    border: 4px solid #FFFFFF;
}
QPushButton#TransportButton,
QPushButton#TransportButton:hover,
QPushButton#TransportButton:pressed,
QPushButton#TransportButton:checked,
QPushButton#TransportButton:checked:hover {
    background: transparent;
    border: none;
}
QSplitter#CaptureVerticalSplitter::handle:vertical {
    background: transparent;
    border: none;
}
QSplitter#CaptureVerticalSplitter::handle:vertical:hover {
    background: #BFC6C3;
    border: none;
}
"""

FRAME_REVIEW_DARK = """
QDialog#FrameReviewDialog {
    background: #050708;
}
QFrame#FrameReviewPanel {
    background: #050708;
    border: none;
}
QFrame#FrameReviewBar {
    background: transparent;
    border: none;
}
QLabel#FrameReviewTitle {
    color: #F4F2EB;
    font-size: 13pt;
    font-weight: 600;
}
QLabel#FrameReviewMeta,
QLabel#FrameReviewZoom {
    color: #D8B365;
    font-size: 10.5pt;
}
QLabel#FrameReviewHint {
    color: #89918F;
    font-size: 9.5pt;
}
QPushButton#FrameReviewAction {
    min-height: 30px;
    padding: 0 8px;
    color: #E8C46F;
    background: transparent;
    border: none;
}
QPushButton#FrameReviewAction:hover {
    color: #F4F2EB;
    background: transparent;
}
QPushButton#FrameReviewClose {
    min-width: 34px;
    max-width: 34px;
    min-height: 32px;
    max-height: 32px;
    padding: 0;
    color: #D8B365;
    background: #101516;
    border: 1px solid #39413F;
    border-radius: 7px;
    font-size: 18pt;
}
QPushButton#FrameReviewClose:hover {
    color: #F4F2EB;
    background: #30251C;
    border-color: #D8B365;
}
QPushButton#FrameReviewNav {
    min-width: 42px;
    max-width: 42px;
    min-height: 56px;
    max-height: 56px;
    padding: 0;
    background: #101516;
    border: 1px solid #27302E;
    border-radius: 9px;
}
QPushButton#FrameReviewNav:hover {
    background: #282315;
    border-color: #D8B365;
}
QPushButton#FrameReviewNav:disabled {
    background: #0B0F10;
    border-color: #171C1C;
}
"""

FRAME_REVIEW_LIGHT = """
QDialog#FrameReviewDialog {
    background: #DDE1DE;
}
QFrame#FrameReviewPanel {
    background: #EDF0ED;
    border: none;
}
QFrame#FrameReviewBar {
    background: transparent;
    border: none;
}
QLabel#FrameReviewTitle {
    color: #303332;
    font-size: 13pt;
    font-weight: 600;
}
QLabel#FrameReviewMeta,
QLabel#FrameReviewZoom {
    color: #A98233;
    font-size: 10.5pt;
}
QLabel#FrameReviewHint {
    color: #777C79;
    font-size: 9.5pt;
}
QPushButton#FrameReviewAction {
    min-height: 30px;
    padding: 0 8px;
    color: #6F5523;
    background: transparent;
    border: none;
}
QPushButton#FrameReviewAction:hover {
    color: #303332;
    background: transparent;
}
QPushButton#FrameReviewClose {
    min-width: 34px;
    max-width: 34px;
    min-height: 32px;
    max-height: 32px;
    padding: 0;
    color: #A98233;
    background: #FFFFFF;
    border: 1px solid #C8CECB;
    border-radius: 7px;
    font-size: 18pt;
}
QPushButton#FrameReviewClose:hover {
    color: #303332;
    background: #F6E8C6;
    border-color: #A98233;
}
QPushButton#FrameReviewNav {
    min-width: 42px;
    max-width: 42px;
    min-height: 56px;
    max-height: 56px;
    padding: 0;
    background: #FFFFFF;
    border: 1px solid #C8CECB;
    border-radius: 9px;
}
QPushButton#FrameReviewNav:hover {
    background: #F6E8C6;
    border-color: #A98233;
}
QPushButton#FrameReviewNav:disabled {
    background: #E7EAE7;
    border-color: #D7DCDA;
}
"""

PERSIAN_FONT_OVERRIDE = """
QWidget, QMainWindow, QDialog, QLabel, QPushButton, QLineEdit, QComboBox,
QTextEdit, QListWidget, QMenu, QToolTip, QRadioButton {
    font-family: "Vazirmatn";
}
QLabel#InspectorTime, QLabel#DetailTime, QLabel#Timecode {
    font-family: "Vazirmatn";
}
"""


def stylesheet(theme: str, language: str = "en") -> str:
    if theme == "light":
        result = (
            LIGHT_STYLESHEET
            + FINAL_LIGHT_OVERRIDES
            + REFERENCE_LIGHT_STYLESHEET
            + FRAME_REVIEW_LIGHT
        )
    else:
        result = (
            APP_STYLESHEET
            + FINAL_DARK_OVERRIDES
            + REFERENCE_DARK_STYLESHEET
            + FRAME_REVIEW_DARK
        )
    if language == "fa":
        result += PERSIAN_FONT_OVERRIDE
    return result
