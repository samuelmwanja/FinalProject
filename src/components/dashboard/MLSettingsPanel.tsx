import React from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Save, AlertTriangle } from "lucide-react";

interface MLSettingsPanelProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onSave?: (settings: MLSettings) => void;
}

interface MLSettings {
  sensitivity: number;
  keywords: string;
  botPatterns: string;
  autoDelete: boolean;
}

const MLSettingsPanel = ({
  open = true,
  onOpenChange = () => {},
  onSave = () => {},
}: MLSettingsPanelProps) => {
  const [showConfirmDialog, setShowConfirmDialog] = React.useState(false);
  const [settings, setSettings] = React.useState<MLSettings>({
    sensitivity: 75,
    keywords: "sub4sub\nfollow me\ncheck my channel\nfree vbucks\nfree robux",
    botPatterns: "^[A-Za-z0-9]+bot$\n.*\\d{3}$",
    autoDelete: false,
  });

  const handleSave = () => {
    setShowConfirmDialog(true);
  };

  const confirmSave = () => {
    onSave(settings);
    setShowConfirmDialog(false);
  };

  return (
    <>
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent className="w-[400px] bg-background" side="right">
          <SheetHeader>
            <SheetTitle>ML Detection Settings</SheetTitle>
          </SheetHeader>

          <div className="mt-6 space-y-6">
            <div className="space-y-2">
              <Label>Detection Sensitivity</Label>
              <Slider
                value={[settings.sensitivity]}
                onValueChange={(value) =>
                  setSettings({ ...settings, sensitivity: value[0] })
                }
                max={100}
                step={1}
              />
              <p className="text-sm text-muted-foreground">
                Current: {settings.sensitivity}% - Higher values will flag more
                comments as spam
              </p>
            </div>

            <div className="space-y-2">
              <Label>Spam Keywords (one per line)</Label>
              <Textarea
                value={settings.keywords}
                onChange={(e) =>
                  setSettings({ ...settings, keywords: e.target.value })
                }
                className="h-[120px]"
                placeholder="Enter keywords..."
              />
            </div>

            <div className="space-y-2">
              <Label>Bot Pattern Detection (RegEx)</Label>
              <Textarea
                value={settings.botPatterns}
                onChange={(e) =>
                  setSettings({ ...settings, botPatterns: e.target.value })
                }
                className="h-[120px]"
                placeholder="Enter regex patterns..."
              />
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                checked={settings.autoDelete}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, autoDelete: checked })
                }
              />
              <Label>Auto-delete high-confidence spam</Label>
            </div>

            <Button className="w-full" onClick={handleSave}>
              <Save className="w-4 h-4 mr-2" />
              Save Settings
            </Button>
          </div>
        </SheetContent>
      </Sheet>

      <AlertDialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Settings Change</AlertDialogTitle>
            <AlertDialogDescription>
              <div className="flex items-center space-x-2 text-yellow-500">
                <AlertTriangle className="w-4 h-4" />
                <span>
                  This will affect how spam is detected across all your videos
                </span>
              </div>
              Are you sure you want to apply these changes?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmSave}>
              Apply Changes
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default MLSettingsPanel; 