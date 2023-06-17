
% Define removeOutliers and drawDotsInstead
removeOutliers = 0; % Change this to 0 if you don't want to remove outliers
drawDotsInstead = 1; % Change this to 1 to plot each (x, y) pair as a dot

% Reading the CSV file
data = readtable('byte_size_duration_with_threshold.csv');

% Extracting data into simple arrays
sizes = data{:,1};
below_threshold_durations = data{:,3};
above_threshold_durations = data{:,4};

% Initializing arrays
byte_sizes = [8, 16, 32, 64, 128, 256];
average_below_threshold_durations = zeros(size(byte_sizes));
average_above_threshold_durations = zeros(size(byte_sizes));
conf_intervals_below_threshold = zeros(size(byte_sizes, 2), 2);
conf_intervals_above_threshold = zeros(size(byte_sizes, 2), 2);

% Looping through the unique sizes
for i = 1:length(byte_sizes)
    % Below threshold
    current_durations_below = below_threshold_durations(sizes == byte_sizes(i));
    current_durations_below = current_durations_below(~isnan(current_durations_below));

    if removeOutliers == 1
        current_durations_below = remove_outliers(current_durations_below);
    end

    average_below_threshold_durations(i) = mean(current_durations_below);
    conf_intervals_below_threshold(i,:) = compute_ci(current_durations_below, 0.95);
    
    % Above threshold
    current_durations_above = above_threshold_durations(sizes == byte_sizes(i));
    current_durations_above = current_durations_above(~isnan(current_durations_above));

    if removeOutliers == 1
        current_durations_above = remove_outliers(current_durations_above);
    end

    average_above_threshold_durations(i) = mean(current_durations_above);
    conf_intervals_above_threshold(i,:) = compute_ci(current_durations_above, 0.95);
end

% Plotting the data
figure; hold on;
if drawDotsInstead == 1
    plot_data(sizes, below_threshold_durations, 'ko');
    plot_data(sizes, above_threshold_durations, 'ro');
else
    plot_data(byte_sizes, average_below_threshold_durations, conf_intervals_below_threshold, 'ko');
    plot_data(byte_sizes, average_above_threshold_durations, conf_intervals_above_threshold, 'ro');
end
hold off;

function ci = compute_ci(data, confidence)
    % Computing the confidence interval
    SEM = std(data)/sqrt(length(data)); % Standard Error
    ts = tinv([(1-confidence)/2  confidence+(1-confidence)/2], length(data)-1); % T-Score
    ci = mean(data) + ts*SEM; % Confidence Intervals
end

function data = remove_outliers(data)
    % Removing outliers
    lower_bound = prctile(data, 25) - 1.5*iqr(data);
    upper_bound = prctile(data, 75) + 1.5*iqr(data);
    data = data(data > lower_bound & data < upper_bound);
end

function plot_data(x, y, marker)
    % Plotting the data with confidence intervals
    plot(x, y, marker, 'MarkerSize', 4, 'LineWidth', 2);

    % Increase the font size
    set(gca, 'FontSize', 16);

    % Setting the axis square
    pbaspect([1 1 1]);

    % Drawing the grid
    grid on; 
    set(gca, 'XMinorGrid', 'off', 'YMinorGrid', 'on'); % Minor grid only on y-axis

    % Labels
    xlabel('Size (B)', 'FontSize', 16);
    ylabel('Duration (ms)', 'FontSize', 16);
end
