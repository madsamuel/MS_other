using System.Drawing;
using System.Text.Json;
using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.Services
{
    public class ResourceService : IResourceService
    {
        public Icon? LoadIcon(string path)
        {
            try
            {
                if (File.Exists(path))
                {
                    return new Icon(path);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading icon: {ex.Message}");
            }
            return null;
        }

        public T? LoadJsonResource<T>(string path) where T : class
        {
            try
            {
                if (File.Exists(path))
                {
                    string json = File.ReadAllText(path);
                    return JsonSerializer.Deserialize<T>(json);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading JSON resource: {ex.Message}");
            }
            return null;
        }
    }
}
