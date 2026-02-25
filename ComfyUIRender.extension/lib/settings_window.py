# -*- coding: utf-8 -*-
"""Settings dialog."""

import os
import clr
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("System.Windows.Forms")

from System.Windows import Window, MessageBox, MessageBoxButton, MessageBoxImage
from System.Windows.Markup import XamlReader
from System.Windows.Forms import OpenFileDialog, DialogResult
import settings_manager

SETTINGS_XAML = """
<Window
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    Title="Settings" Height="420" Width="500"
    WindowStartupLocation="CenterOwner"
    Background="#1A1A2E" ResizeMode="NoResize">

    <Window.Resources>
        <Style TargetType="TextBlock">
            <Setter Property="Foreground" Value="#9090B0"/>
            <Setter Property="FontSize" Value="11"/>
            <Setter Property="Margin" Value="0,10,0,3"/>
        </Style>
        <Style TargetType="TextBox">
            <Setter Property="Background" Value="#1E1E32"/>
            <Setter Property="Foreground" Value="#E8E8F0"/>
            <Setter Property="BorderBrush" Value="#3A3A5C"/>
            <Setter Property="BorderThickness" Value="1"/>
            <Setter Property="Padding" Value="8,6"/>
            <Setter Property="FontSize" Value="12"/>
            <Setter Property="CaretBrush" Value="White"/>
        </Style>
        <Style x:Key="Btn" TargetType="Button">
            <Setter Property="Background" Value="#6C63FF"/>
            <Setter Property="Foreground" Value="White"/>
            <Setter Property="FontSize" Value="12"/>
            <Setter Property="FontWeight" Value="SemiBold"/>
            <Setter Property="BorderThickness" Value="0"/>
            <Setter Property="Cursor" Value="Hand"/>
            <Setter Property="Padding" Value="16,8"/>
            <Setter Property="Template">
                <Setter.Value>
                    <ControlTemplate TargetType="Button">
                        <Border Background="{TemplateBinding Background}"
                                CornerRadius="6" Padding="{TemplateBinding Padding}">
                            <ContentPresenter HorizontalAlignment="Center"
                                              VerticalAlignment="Center"/>
                        </Border>
                        <ControlTemplate.Triggers>
                            <Trigger Property="IsMouseOver" Value="True">
                                <Setter Property="Background" Value="#7C73FF"/>
                            </Trigger>
                        </ControlTemplate.Triggers>
                    </ControlTemplate>
                </Setter.Value>
            </Setter>
        </Style>
        <Style x:Key="SecBtn" TargetType="Button" BasedOn="{StaticResource Btn}">
            <Setter Property="Background" Value="#2E2E4A"/>
        </Style>
    </Window.Resources>

    <StackPanel Margin="24">
        <TextBlock Text="Settings" Foreground="#E8E8F0" FontSize="18"
                   FontWeight="Bold" Margin="0,0,0,14"/>

        <TextBlock Text="ComfyUI URL"/>
        <TextBox x:Name="UrlBox"/>

        <TextBlock Text="Model Name (.ckpt or .safetensors filename in ComfyUI models folder)"/>
        <TextBox x:Name="ModelBox"/>

        <TextBlock Text="Workflow JSON path  (optional — leave blank to use built-in workflow)"/>
        <Grid>
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="8"/>
                <ColumnDefinition Width="80"/>
            </Grid.ColumnDefinitions>
            <TextBox x:Name="WorkflowBox" Grid.Column="0"/>
            <Button x:Name="BrowseBtn" Grid.Column="2"
                    Content="Browse" Style="{StaticResource SecBtn}" Padding="0,8"/>
        </Grid>

        <Grid Margin="0,12,0,0">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="12"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="12"/>
                <ColumnDefinition Width="*"/>
            </Grid.ColumnDefinitions>
            <StackPanel Grid.Column="0">
                <TextBlock Text="Steps" Margin="0,0,0,3"/>
                <TextBox x:Name="StepsBox"/>
            </StackPanel>
            <StackPanel Grid.Column="2">
                <TextBlock Text="CFG Scale" Margin="0,0,0,3"/>
                <TextBox x:Name="CfgBox"/>
            </StackPanel>
            <StackPanel Grid.Column="4">
                <TextBlock Text="Denoise" Margin="0,0,0,3"/>
                <TextBox x:Name="DenoiseBox"/>
            </StackPanel>
        </Grid>

        <Button x:Name="SaveBtn" Content="Save Settings"
                Style="{StaticResource Btn}"
                HorizontalAlignment="Right" Margin="0,24,0,0"/>
    </StackPanel>
</Window>
"""


class SettingsWindow(object):
    def __init__(self, owner=None):
        self._win = XamlReader.Parse(SETTINGS_XAML)
        if owner:
            self._win.Owner = owner

        self._url_box      = self._win.FindName("UrlBox")
        self._model_box    = self._win.FindName("ModelBox")
        self._workflow_box = self._win.FindName("WorkflowBox")
        self._steps_box    = self._win.FindName("StepsBox")
        self._cfg_box      = self._win.FindName("CfgBox")
        self._denoise_box  = self._win.FindName("DenoiseBox")

        self._win.FindName("BrowseBtn").Click += self._browse
        self._win.FindName("SaveBtn").Click   += self._save

        self._load()

    def show(self):
        self._win.ShowDialog()

    def _load(self):
        s = settings_manager.load()
        self._url_box.Text      = s.get("comfy_url", "http://127.0.0.1:8000")
        self._model_box.Text    = s.get("model_name", "")
        self._workflow_box.Text = s.get("workflow_path", "")
        self._steps_box.Text    = str(s.get("steps", 20))
        self._cfg_box.Text      = str(s.get("cfg_scale", 7.0))
        self._denoise_box.Text  = str(s.get("denoise", 0.75))

    def _browse(self, sender, e):
        dlg = OpenFileDialog()
        dlg.Title  = "Select ComfyUI Workflow JSON"
        dlg.Filter = "JSON files|*.json|All files|*.*"
        if dlg.ShowDialog() == DialogResult.OK:
            self._workflow_box.Text = dlg.FileName

    def _save(self, sender, e):
        s = settings_manager.load()
        s["comfy_url"]     = self._url_box.Text.strip().rstrip("/")
        s["model_name"]    = self._model_box.Text.strip()
        s["workflow_path"] = self._workflow_box.Text.strip()
        try:    s["steps"]     = int(self._steps_box.Text)
        except: pass
        try:    s["cfg_scale"] = float(self._cfg_box.Text)
        except: pass
        try:    s["denoise"]   = float(self._denoise_box.Text)
        except: pass
        settings_manager.save(s)
        MessageBox.Show("Settings saved!", "ComfyUI Render",
                        MessageBoxButton.OK, MessageBoxImage.Information)
        self._win.Close()
