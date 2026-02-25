# -*- coding: utf-8 -*-
"""render_window.py - Non-modal WPF UI. Settings panel inline, no popup windows."""

import os, sys, json, uuid, threading, tempfile, glob

import clr
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
clr.AddReference("System")
clr.AddReference("System.Windows.Forms")

import System
from System import Action
from System.Windows import (
    Visibility, MessageBox, MessageBoxButton, MessageBoxImage
)
from System.Windows.Markup import XamlReader
from System.Windows.Media.Imaging import BitmapImage, BitmapCacheOption
from System.Windows.Forms import SaveFileDialog, DialogResult

import settings_manager
import comfy_http
import app_state

WINDOW_XAML = r"""
<Window
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Title="ComfyUI Render"
    Height="820" Width="1100"
    MinHeight="600" MinWidth="800"
    WindowStartupLocation="CenterScreen"
    Background="#1A1A2E">
  <Window.Resources>
    <Style x:Key="PBtn" TargetType="Button">
      <Setter Property="Background" Value="#6C63FF"/>
      <Setter Property="Foreground" Value="White"/>
      <Setter Property="FontSize" Value="13"/>
      <Setter Property="FontWeight" Value="SemiBold"/>
      <Setter Property="Padding" Value="18,10"/>
      <Setter Property="BorderThickness" Value="0"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="bd" Background="{TemplateBinding Background}" CornerRadius="8" Padding="{TemplateBinding Padding}">
              <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True"><Setter TargetName="bd" Property="Background" Value="#7C73FF"/></Trigger>
              <Trigger Property="IsPressed"   Value="True"><Setter TargetName="bd" Property="Background" Value="#5A52DD"/></Trigger>
              <Trigger Property="IsEnabled"   Value="False">
                <Setter TargetName="bd" Property="Background" Value="#2A2A44"/>
                <Setter Property="Foreground" Value="#555570"/>
              </Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
    <Style x:Key="SBtn" TargetType="Button" BasedOn="{StaticResource PBtn}">
      <Setter Property="Background" Value="#252538"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="bd" Background="{TemplateBinding Background}" CornerRadius="8" Padding="{TemplateBinding Padding}">
              <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True"><Setter TargetName="bd" Property="Background" Value="#333350"/></Trigger>
              <Trigger Property="IsEnabled"   Value="False">
                <Setter TargetName="bd" Property="Background" Value="#1E1E30"/>
                <Setter Property="Foreground" Value="#444460"/>
              </Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
    <Style x:Key="DBtn" TargetType="Button" BasedOn="{StaticResource PBtn}">
      <Setter Property="Background" Value="#7A1F1F"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="bd" Background="{TemplateBinding Background}" CornerRadius="8" Padding="{TemplateBinding Padding}">
              <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True"><Setter TargetName="bd" Property="Background" Value="#AA2222"/></Trigger>
              <Trigger Property="IsEnabled"   Value="False">
                <Setter TargetName="bd" Property="Background" Value="#2A1A1A"/>
                <Setter Property="Foreground" Value="#664444"/>
              </Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
    <Style x:Key="Field" TargetType="TextBox">
      <Setter Property="Background" Value="#12122A"/>
      <Setter Property="Foreground" Value="#E8E8F0"/>
      <Setter Property="BorderBrush" Value="#3A3A5C"/>
      <Setter Property="BorderThickness" Value="1"/>
      <Setter Property="Padding" Value="10,8"/>
      <Setter Property="FontSize" Value="12"/>
      <Setter Property="CaretBrush" Value="White"/>
    </Style>
    <Style x:Key="Label" TargetType="TextBlock">
      <Setter Property="Foreground" Value="#7070A0"/>
      <Setter Property="FontSize" Value="11"/>
      <Setter Property="FontWeight" Value="SemiBold"/>
      <Setter Property="Margin" Value="0,0,0,4"/>
    </Style>
  </Window.Resources>

  <Grid>

    <!-- ══ MAIN PANEL ══════════════════════════════════════════════════════ -->
    <Grid x:Name="MainPanel">
      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="2*"/>  <!-- left: large render output -->
        <ColumnDefinition Width="*"/>   <!-- right: controls -->
      </Grid.ColumnDefinitions>

      <!-- ── LEFT: render output fills entire panel ── -->
      <Border Grid.Column="0" Background="#0C0C1E" Margin="12,12,6,12">
        <Grid>
          <TextBlock x:Name="ResultHint"
                     Text="Rendered result will appear here"
                     Foreground="#303055" FontSize="14"
                     HorizontalAlignment="Center" VerticalAlignment="Center"/>
          <Viewbox x:Name="ResultViewbox" Stretch="Uniform" Visibility="Collapsed">
            <Image x:Name="ResultImg" Width="1280" Height="1280"/>
          </Viewbox>
        </Grid>
      </Border>

      <!-- ── RIGHT: controls ── -->
      <Grid Grid.Column="1" Margin="6,12,12,12">
        <Grid.RowDefinitions>
          <RowDefinition Height="Auto"/>  <!-- 0 header       -->
          <RowDefinition Height="160"/>   <!-- 1 snapshot      -->
          <RowDefinition Height="Auto"/>  <!-- 2 prompt label  -->
          <RowDefinition Height="100"/>   <!-- 3 prompt box    -->
          <RowDefinition Height="Auto"/>  <!-- 4 buttons       -->
          <RowDefinition Height="Auto"/>  <!-- 5 status        -->
          <RowDefinition Height="*"/>     <!-- 6 spacer        -->
          <RowDefinition Height="Auto"/>  <!-- 7 save buttons  -->
        </Grid.RowDefinitions>

        <!-- Header -->
        <StackPanel Grid.Row="0" Orientation="Horizontal" Margin="0,0,0,10">
          <TextBlock Text="&#x26A1;" FontSize="18" Foreground="#6C63FF"
                     VerticalAlignment="Center" Margin="0,0,6,0"/>
          <TextBlock Text="ComfyUI Render" Foreground="#E8E8F0"
                     FontSize="15" FontWeight="Bold" VerticalAlignment="Center"/>
        </StackPanel>

        <!-- Snapshot — exact v16 Viewbox pattern -->
        <Border Grid.Row="1" Background="#0C0C1E" CornerRadius="8"
                BorderBrush="#2A2A50" BorderThickness="1" Margin="0,0,0,10">
          <Grid>
            <TextBlock x:Name="SnapHint" Text="3D View Snapshot"
                       Foreground="#303055" FontSize="12"
                       HorizontalAlignment="Center" VerticalAlignment="Center"/>
            <Viewbox x:Name="SnapViewbox" Stretch="Uniform" Visibility="Collapsed">
              <Image x:Name="SnapImg" Width="1366" Height="768"/>
            </Viewbox>
          </Grid>
        </Border>

        <!-- Prompt label -->
        <TextBlock Grid.Row="2" Text="PROMPT" Style="{StaticResource Label}"/>

        <!-- Prompt box -->
        <TextBox x:Name="PromptBox" Grid.Row="3"
                 Background="#12122A" Foreground="#E8E8F0"
                 BorderBrush="#6C63FF" BorderThickness="1"
                 FontSize="12" Padding="10,8" CaretBrush="#9090FF"
                 TextWrapping="Wrap" AcceptsReturn="True"
                 VerticalScrollBarVisibility="Auto"
                 Text="architectural visualisation, ultra realistic, high detail, cinematic lighting"
                 Margin="0,0,0,10"/>

        <!-- Buttons -->
        <StackPanel Grid.Row="4" Margin="0,0,0,10">
          <Grid Margin="0,0,0,6">
            <Grid.ColumnDefinitions>
              <ColumnDefinition Width="*"/>
              <ColumnDefinition Width="6"/>
              <ColumnDefinition Width="Auto"/>
            </Grid.ColumnDefinitions>
            <Button x:Name="RenderBtn" Grid.Column="0" Content="Render"
                    Style="{StaticResource PBtn}"/>
            <Button x:Name="StopBtn"   Grid.Column="2" Content="Stop"
                    Style="{StaticResource DBtn}" Visibility="Collapsed"/>
          </Grid>
          <Button x:Name="SettingsBtn" Content="Settings"
                  Style="{StaticResource SBtn}" FontSize="11"/>
        </StackPanel>

        <!-- Status -->
        <Border Grid.Row="5" Background="#0C0C1E" CornerRadius="8" Padding="10,6">
          <StackPanel Orientation="Horizontal">
            <TextBlock x:Name="StatusIcon" Text="OK" Foreground="#55CC88"
                       FontSize="11" Margin="0,0,6,0"/>
            <TextBlock x:Name="StatusMsg" Foreground="#7070A0" FontSize="11"
                       VerticalAlignment="Center" TextWrapping="Wrap" Text="Ready."/>
          </StackPanel>
        </Border>

        <!-- Save / Open -->
        <StackPanel Grid.Row="7" Margin="0,0,0,0">
          <Button x:Name="SaveBtn" Content="Save Image"
                  Style="{StaticResource PBtn}" Margin="0,0,0,6"
                  Visibility="Collapsed"/>
          <Button x:Name="OpenViewerBtn" Content="Open in Viewer"
                  Style="{StaticResource SBtn}"
                  Visibility="Collapsed"/>
        </StackPanel>

      </Grid>
    </Grid>

    <!-- ══ SETTINGS PANEL ═════════════════════════════════════════════════ -->
    <Grid x:Name="SettingsPanel" Visibility="Collapsed" Margin="18">
      <Grid.RowDefinitions>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="*"/>
        <RowDefinition Height="Auto"/>
      </Grid.RowDefinitions>

      <StackPanel Grid.Row="0" Orientation="Horizontal" Margin="0,0,0,20">
        <TextBlock Text="&#x2699;" FontSize="20" Foreground="#6C63FF"
                   VerticalAlignment="Center" Margin="0,0,8,0"/>
        <TextBlock Text="Settings" Foreground="#E8E8F0"
                   FontSize="18" FontWeight="Bold" VerticalAlignment="Center"/>
      </StackPanel>

      <StackPanel Grid.Row="1">
        <TextBlock Text="COMFYUI URL" Style="{StaticResource Label}"/>
        <TextBox x:Name="UrlBox" Style="{StaticResource Field}" Margin="0,0,0,16"/>
        <TextBlock Text="PORT" Style="{StaticResource Label}"/>
        <TextBox x:Name="PortBox" Style="{StaticResource Field}" Margin="0,0,0,16"/>
        <Border Background="#0C0C1E" CornerRadius="8" Padding="14,10" Margin="0,8,0,0">
          <TextBlock x:Name="SettingsStatus" Text="" Foreground="#55CC88"
                     FontSize="12" TextWrapping="Wrap"/>
        </Border>
      </StackPanel>

      <Grid Grid.Row="2" Margin="0,16,0,0">
        <Grid.ColumnDefinitions>
          <ColumnDefinition Width="*"/>
          <ColumnDefinition Width="8"/>
          <ColumnDefinition Width="Auto"/>
        </Grid.ColumnDefinitions>
        <Button x:Name="SaveSettingsBtn" Grid.Column="0" Content="Save Settings"
                Style="{StaticResource PBtn}"/>
        <Button x:Name="BackBtn" Grid.Column="2" Content="Back"
                Style="{StaticResource SBtn}"/>
      </Grid>
    </Grid>

  </Grid>
</Window>
"""



class RenderWindow(object):

    def __init__(self, snapshot_path, uidoc=None):
        self._uidoc         = uidoc
        self._snapshot_path = snapshot_path
        self._result_tmp    = None

        self._win = XamlReader.Parse(WINDOW_XAML)

        # Main panel elements
        self._main_panel   = self._win.FindName("MainPanel")
        self._snap_hint    = self._win.FindName("SnapHint")
        self._snap_viewbox = self._win.FindName("SnapViewbox")
        self._snap_img     = self._win.FindName("SnapImg")
        self._prompt_box   = self._win.FindName("PromptBox")
        self._render_btn   = self._win.FindName("RenderBtn")
        self._stop_btn     = self._win.FindName("StopBtn")
        self._settings_btn = self._win.FindName("SettingsBtn")
        self._status_icon  = self._win.FindName("StatusIcon")
        self._status_msg   = self._win.FindName("StatusMsg")
        self._result_hint  = self._win.FindName("ResultHint")
        self._result_img     = self._win.FindName("ResultImg")
        self._result_viewbox = self._win.FindName("ResultViewbox")
        self._save_btn     = self._win.FindName("SaveBtn")
        self._open_btn     = self._win.FindName("OpenViewerBtn")

        # Settings panel elements
        self._settings_panel  = self._win.FindName("SettingsPanel")
        self._url_box         = self._win.FindName("UrlBox")
        self._port_box        = self._win.FindName("PortBox")
        self._settings_status = self._win.FindName("SettingsStatus")

        # Wire up events
        self._render_btn.Click      += self._on_render
        self._stop_btn.Click        += self._on_stop
        self._settings_btn.Click    += self._show_settings
        self._save_btn.Click        += self._on_save
        self._open_btn.Click        += self._on_open_viewer
        self._win.FindName("SaveSettingsBtn").Click += self._save_settings
        self._win.FindName("BackBtn").Click         += self._hide_settings

        app_state.clear_stop()
        self._load_snapshot_file(snapshot_path)
        self._set_status("OK", "Ready.")

    def show(self):
        self._win.Show()

    # ── Public: called by Start ribbon if window already open ─────────────

    def update_snapshot(self, path):
        self._snapshot_path = path
        self._load_snapshot_file(path)
        self._set_status("OK", "Snapshot updated.")

    # ── Status ────────────────────────────────────────────────────────────

    def _set_status(self, icon, msg):
        def _do():
            self._status_icon.Text = icon
            self._status_msg.Text  = msg
        self._win.Dispatcher.Invoke(Action(_do))

    # ── Load snapshot ─────────────────────────────────────────────────────

    def _load_snapshot_file(self, path):
        if not path or not os.path.exists(path):
            self._set_status("ERR", "Snapshot not found.")
            return
        try:
            uri_str = "file:///" + path.replace("\\", "/")
            bmp = BitmapImage()
            bmp.BeginInit()
            bmp.UriSource     = System.Uri(uri_str)
            bmp.CacheOption   = BitmapCacheOption.OnLoad
            bmp.CreateOptions = System.Windows.Media.Imaging.BitmapCreateOptions.IgnoreImageCache
            bmp.EndInit()
            bmp.Freeze()
            def _do():
                self._snap_img.Source        = bmp
                self._snap_viewbox.Visibility = Visibility.Visible
                self._snap_hint.Visibility    = Visibility.Collapsed
            self._win.Dispatcher.Invoke(Action(_do))
        except Exception as ex:
            self._set_status("WARN", "Preview error: " + str(ex))

    # ── Settings panel ────────────────────────────────────────────────────

    def _show_settings(self, sender, e):
        # Load current settings into fields
        s    = settings_manager.load()
        url  = s.get("comfy_url", "http://127.0.0.1:8000")
        # Split URL into host and port
        try:
            parts = url.rsplit(":", 1)
            host  = parts[0]
            port  = parts[1].rstrip("/")
        except Exception:
            host = url
            port = "8000"
        self._url_box.Text          = host
        self._port_box.Text         = port
        self._settings_status.Text  = ""
        self._main_panel.Visibility    = Visibility.Collapsed
        self._settings_panel.Visibility = Visibility.Visible

    def _hide_settings(self, sender, e):
        self._settings_panel.Visibility = Visibility.Collapsed
        self._main_panel.Visibility     = Visibility.Visible

    def _save_settings(self, sender, e):
        host = self._url_box.Text.strip().rstrip("/")
        port = self._port_box.Text.strip()
        if not host:
            self._settings_status.Text = "URL cannot be empty."
            return
        if not port.isdigit():
            self._settings_status.Text = "Port must be a number."
            return
        full_url = "{0}:{1}".format(host, port)
        s = settings_manager.load()
        s["comfy_url"] = full_url
        settings_manager.save(s)
        # Test connection
        ok, msg = comfy_http.test_connection(full_url)
        if ok:
            self._settings_status.Text = "Saved. Connected to ComfyUI successfully."
        else:
            self._settings_status.Text = "Saved. Warning: " + msg
        # Go back after short delay would need threading — just show message
        # User clicks Back when ready

    # ── Stop ──────────────────────────────────────────────────────────────

    def _on_stop(self, sender, e):
        app_state.request_stop()
        try:
            s = settings_manager.load()
            comfy_http.post_json(s["comfy_url"].rstrip("/"), "/interrupt", {})
        except Exception:
            pass
        self._set_status("STOP", "Stopping...")

    # ── Render ────────────────────────────────────────────────────────────

    def _on_render(self, sender, e):
        if not self._snapshot_path or not os.path.exists(self._snapshot_path):
            MessageBox.Show("No snapshot. Click Start in the Revit ribbon first.",
                "ComfyUI Render", MessageBoxButton.OK, MessageBoxImage.Warning)
            return

        prompt = self._prompt_box.Text.strip()
        if not prompt:
            MessageBox.Show("Please enter a prompt.",
                "ComfyUI Render", MessageBoxButton.OK, MessageBoxImage.Warning)
            return

        snapshot = self._snapshot_path
        app_state.clear_stop()

        def _set_rendering(on):
            self._render_btn.IsEnabled = not on
            self._stop_btn.Visibility  = Visibility.Visible if on else Visibility.Collapsed
            self._settings_btn.IsEnabled = not on

        self._win.Dispatcher.Invoke(Action(lambda: _set_rendering(True)))

        def _worker():
            try:
                s        = settings_manager.load()
                base_url = s["comfy_url"].rstrip("/")

                self._set_status("...", "Connecting...")
                ok, msg = comfy_http.test_connection(base_url)
                if not ok:
                    raise Exception(msg)
                if app_state.stop_requested:
                    raise Exception("Stopped.")

                self._set_status("...", "Encoding snapshot...")
                b64 = comfy_http.image_to_base64(snapshot)
                if app_state.stop_requested:
                    raise Exception("Stopped.")

                self._set_status("...", "Sending: " + prompt[:50] + "...")
                from workflow import build as build_workflow
                wf     = build_workflow(b64, prompt)
                result = comfy_http.post_json(base_url, "/prompt", {
                    "prompt":    wf,
                    "client_id": str(uuid.uuid4()).replace("-", "")
                })
                if "prompt_id" not in result:
                    raise Exception("No prompt_id. Got: " + str(result)[:300])

                prompt_id   = result["prompt_id"]
                output_file = self._poll(base_url, prompt_id)
                if app_state.stop_requested:
                    raise Exception("Stopped.")

                self._set_status("...", "Downloading...")
                data = comfy_http.download_image(base_url, output_file)
                self._show_result(data)
                self._set_status("OK", "Done! Click Save to export.")

            except Exception as ex:
                msg = str(ex)
                if "Stopped" in msg:
                    self._set_status("STOP", "Render stopped.")
                else:
                    self._set_status("ERR", msg)
                    e2 = msg
                    self._win.Dispatcher.Invoke(Action(lambda:
                        MessageBox.Show("Render failed:\n\n" + e2,
                            "ComfyUI Render", MessageBoxButton.OK, MessageBoxImage.Error)))
            finally:
                app_state.clear_stop()
                self._win.Dispatcher.Invoke(Action(lambda: _set_rendering(False)))

        t = threading.Thread(target=_worker)
        t.daemon = True
        t.start()

    # ── Poll ──────────────────────────────────────────────────────────────

    def _poll(self, base_url, prompt_id):
        import time
        for i in range(120):
            if app_state.stop_requested:
                raise Exception("Stopped.")
            time.sleep(5)
            self._set_status("...", "Rendering... ({0}s)".format((i + 1) * 5))
            data = comfy_http.get_json("{0}/history/{1}".format(base_url, prompt_id))
            if prompt_id in data:
                all_imgs = []
                for node_out in data[prompt_id].get("outputs", {}).values():
                    for img in node_out.get("images", []):
                        all_imgs.append(img)
                if all_imgs:
                    for img in all_imgs:
                        if img.get("type", "") == "output":
                            return img["filename"]
                    return all_imgs[0]["filename"]
        raise Exception("Timed out.")

    # ── Show result ───────────────────────────────────────────────────────

    def _show_result(self, data):
        try:
            import time
            tmp_dir = os.path.join(tempfile.gettempdir(), "RevitComfyUI")
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            tmp = os.path.join(tmp_dir, "result_{0}.png".format(int(time.time())))
            for old_f in glob.glob(os.path.join(tmp_dir, "result_*.png")):
                try: os.remove(old_f)
                except: pass

            f = open(tmp, "wb")
            try:    f.write(bytes(data))
            except: f.write(bytearray([b for b in data]))
            f.close()
            self._result_tmp = tmp

            uri_str = "file:///" + tmp.replace("\\", "/")
            bmp = BitmapImage()
            bmp.BeginInit()
            bmp.UriSource     = System.Uri(uri_str)
            bmp.CacheOption   = BitmapCacheOption.OnLoad
            bmp.CreateOptions = System.Windows.Media.Imaging.BitmapCreateOptions.IgnoreImageCache
            bmp.EndInit()
            bmp.Freeze()

            def _do():
                self._result_img.Source         = bmp
                self._result_viewbox.Visibility = Visibility.Visible
                self._result_hint.Visibility    = Visibility.Collapsed
                self._save_btn.Visibility       = Visibility.Visible
                self._open_btn.Visibility       = Visibility.Visible
            self._win.Dispatcher.Invoke(Action(_do))
        except Exception as ex:
            self._set_status("ERR", "Display error: " + str(ex))

    # ── Save ──────────────────────────────────────────────────────────────

    def _on_save(self, sender, e):
        import shutil
        if not self._result_tmp or not os.path.exists(self._result_tmp):
            self._set_status("ERR", "No result to save.")
            return
        dlg = SaveFileDialog()
        dlg.Title    = "Save Rendered Image"
        dlg.Filter   = "PNG Image|*.png"
        dlg.FileName = "ComfyUI_Render"
        if dlg.ShowDialog() == DialogResult.OK:
            try:
                shutil.copy2(self._result_tmp, dlg.FileName)
                self._set_status("OK", "Saved: " + dlg.FileName)
            except Exception as ex:
                self._set_status("ERR", "Save failed: " + str(ex))

    # ── Open viewer ───────────────────────────────────────────────────────

    def _on_open_viewer(self, sender, e):
        if self._result_tmp and os.path.exists(self._result_tmp):
            try:    os.startfile(self._result_tmp)
            except Exception as ex:
                self._set_status("ERR", "Could not open: " + str(ex))


def show_window(snapshot_path, uidoc=None):
    w = RenderWindow(snapshot_path, uidoc=uidoc)
    app_state.window = w
    w.show()
