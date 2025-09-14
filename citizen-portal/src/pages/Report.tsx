import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from "@/components/ui/form";
import { Send, ArrowLeft, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import Layout from "@/components/Layout";
import LocationPicker from "@/components/LocationPicker";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { submitNewReport } from "@/lib/api";

const reportSchema = z.object({
  description: z.string().min(10, { message: "Description must be at least 10 characters." }).max(500, { message: "Description must be 500 characters or less." }),
  latitude: z.number({ required_error: "Please select a location on the map." }).min(-90).max(90),
  longitude: z.number({ required_error: "Please select a location on the map." }).min(-180).max(180),
  file: z.instanceof(FileList).optional()
    .refine(files => !files || files.length === 0 || files[0].size <= 5 * 1024 * 1024, `Max file size is 5MB.`)
    .refine(
      files => !files || files.length === 0 || ["image/jpeg", "image/png", "image/webp"].includes(files[0].type),
      "Only .jpg, .png, and .webp formats are supported."
    ),
});

// Create a type that ensures all required fields are present
type ValidatedReportData = {
  description: string;
  latitude: number;
  longitude: number;
  file?: FileList;
};

const Report = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const form = useForm<z.infer<typeof reportSchema>>({
    resolver: zodResolver(reportSchema),
    defaultValues: {
      description: "",
      latitude: undefined,
      longitude: undefined,
    },
  });

  const { formState: { isSubmitting } } = form;

  const handleLocationSelect = (lat: number, lng: number) => {
    const latitude = parseFloat(lat.toFixed(6));
    const longitude = parseFloat(lng.toFixed(6));
    
    // Batch the form updates to prevent multiple re-renders
    form.setValue("latitude", latitude, { shouldValidate: false });
    form.setValue("longitude", longitude, { shouldValidate: false });
    
    // Clear any existing location validation errors
    form.clearErrors(["latitude", "longitude"]);
    
    // Trigger validation for the location fields after setting values
    setTimeout(() => {
      form.trigger(["latitude", "longitude"]);
    }, 0);
  };

  const onSubmit = async (values: z.infer<typeof reportSchema>) => {
    // Ensure all required fields are present for TypeScript
    if (!values.description || values.latitude === undefined || values.longitude === undefined) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields including location.",
        variant: "destructive",
      });
      return;
    }

    try {
      const reportData = {
        description: values.description,
        latitude: values.latitude,
        longitude: values.longitude,
        file: values.file
      };
      
      await submitNewReport(reportData);
      toast({
        title: "Report Submitted Successfully",
        description: "Thank you for helping improve your community.",
      });
      navigate('/my-reports');
    } catch (error) {
      toast({
        title: "Submission Failed",
        description: (error as Error).message || "Could not submit your report. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/home')}
            className="flex items-center space-x-2 mb-4"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Home</span>
          </Button>
          <h1 className="text-3xl font-bold">Report a Civic Issue</h1>
          <p className="text-muted-foreground mt-2">
            Help us improve your community by reporting infrastructure problems, safety concerns, or public service issues.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Issue Details</CardTitle>
            <CardDescription>
              Please provide as much detail as possible to help us address the issue effectively.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Issue Description *</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Describe the issue in detail..."
                          className="min-h-[120px] resize-none"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="file"
                  render={({ field }) => (
                    <FormItem>
                       <FormLabel>Photo Evidence (Optional)</FormLabel>
                       <FormControl>
                          <Input type="file" accept="image/jpeg,image/png,image/webp" {...form.register("file")} />
                       </FormControl>
                       <FormDescription>Max file size: 5MB. Accepted formats: JPG, PNG, WebP.</FormDescription>
                       <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="space-y-4">
                  <FormLabel>Issue Location *</FormLabel>
                  <FormDescription>
                    Click on the map to pinpoint where the issue is located, or use "Use My Location" to automatically detect your current position.
                  </FormDescription>
                  <LocationPicker 
                    onLocationSelect={handleLocationSelect}
                    initialPosition={form.watch("latitude") && form.watch("longitude") ? 
                      [form.watch("latitude"), form.watch("longitude")] : undefined
                    }
                  />
                  {/* Only show validation errors if the form has been touched and has errors */}
                  {(form.formState.errors.latitude || form.formState.errors.longitude) && 
                   (form.formState.touchedFields.latitude || form.formState.touchedFields.longitude) && (
                    <div className="bg-red-50 border border-red-200 rounded-md p-3">
                      <p className="text-sm font-medium text-destructive flex items-center gap-2">
                        <AlertCircle className="h-4 w-4 flex-shrink-0" />
                        {form.formState.errors.latitude?.message || form.formState.errors.longitude?.message}
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => navigate('/home')} disabled={isSubmitting}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={isSubmitting}>
                    <Send className="h-4 w-4 mr-2" />
                    {isSubmitting ? "Submitting..." : "Submit Report"}
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Report;