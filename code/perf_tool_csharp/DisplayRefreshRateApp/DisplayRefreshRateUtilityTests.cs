using System;
using Xunit;

public class DisplayRefreshRateUtilityTests
{
    [Fact]
    public void EnumDisplaySettings_Returns_Valid_RefreshRate()
    {
        // Arrange
        var devMode = new DisplayRefreshRateUtility.DEVMODE();
        devMode.dmSize = (ushort)System.Runtime.InteropServices.Marshal.SizeOf(typeof(DisplayRefreshRateUtility.DEVMODE));

        // Act
        bool result = DisplayRefreshRateUtility.EnumDisplaySettings(null, -1, ref devMode);

        // Assert
        Assert.True(result); // Should succeed on a Windows system
        Assert.InRange(devMode.dmDisplayFrequency, 1, 1000); // Typical refresh rates are between 1 and 1000 Hz
    }
}
