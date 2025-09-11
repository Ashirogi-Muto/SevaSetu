import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from "@/components/ui/form";
import { Upload, MapPin, Send, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import Layout from "@/components/Layout";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { submitNewReport } from "@/lib/api"; // Added this import

const reportSchema = z.object({
  description: z.string().min(10, { message: "Description must be at least 10 characters." }).max(500, { message: "Description must be 500 characters or less." }),
  latitude: z.coerce.number({ required_error: "Latitude is required." }).min(-90).max(90),
  longitude: z.coerce.number({ required_error: "Longitude is required." }).min(-180).max(180),
  file: z.instanceof(FileList).optional()
    .refine(files => !files || files.length === 0 || files[0].size <= 5 * 1024 * 1024, `Max file size is 5MB.`)
    .refine(
      files => !files || files.length === 0 || ["image/jpeg", "image/png", "image/webp"].includes(files[0].type),
      "Only .jpg, .png, and .webp formats are supported."
    ),
});

const Report = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const form = useForm<z.infer<typeof reportSchema>>({
    resolver: zodResolver(reportSchema),
    defaultValues: {
      description: "",
    },
  });

  const { formState: { isSubmitting } } = form;

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          form.setValue("latitude", parseFloat(position.coords.latitude.toFixed(6)));
          form.setValue("longitude", parseFloat(position.coords.longitude.toFixed(6)));
          toast({
            title: "Location Obtained",
            description: "Your current location has been filled in.",
          });
        },
        (error) => {
          toast({
            title: "Location Error",
            description: "Unable to get your location. Please enter manually.",
            variant: "destructive",
          });
        }
      );
    } else {
      toast({
        title: "Geolocation Not Supported",
        description: "Please enter your location manually",
        variant: "destructive",
      });
    }
  };

  const onSubmit = async (values: z.infer<typeof reportSchema>) => {
    try {
      await submitNewReport(values);
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
                  <div className="flex items-center justify-between">
                    <FormLabel>Location Coordinates *</FormLabel>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={getCurrentLocation}
                    >
                      <MapPin className="h-4 w-4 mr-2" />
                      <span>Use Current Location</span>
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="latitude"
                      render={({ field }) => (
                        <FormItem>
                           <FormLabel>Latitude</FormLabel>
                           <FormControl>
                              <Input type="number" step="any" placeholder="e.g., 40.712800" {...field} />
                           </FormControl>
                           <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="longitude"
                      render={({ field }) => (
                        <FormItem>
                           <FormLabel>Longitude</FormLabel>
                           <FormControl>
                              <Input type="number" step="any" placeholder="e.g., -74.006000" {...field} />
                           </FormControl>
                           <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
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