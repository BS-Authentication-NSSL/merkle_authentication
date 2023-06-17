% Define removeOutliers
removeOutliers = 1; % Change this to 0 if you don't want to remove outliers

% Reading the CSV file
data = readtable('byte_size_duration.csv');

% Extracting data into simple arrays
sizes = data{:,1};
durations = data{:,2};

% Initializing arrays
byte_sizes = [8, 16, 32, 64, 128, 256];
average_durations = zeros(size(byte_sizes));
conf_intervals = zeros(size(byte_sizes, 2), 2);

% Looping through the unique sizes
for i = 1:length(byte_sizes)
    current_durations = durations(sizes == byte_sizes(i));

    if removeOutliers == 1
        current_durations = remove_outliers(current_durations);
    end

    average_durations(i) = mean(current_durations);
    conf_intervals(i,:) = compute_ci(current_durations, 0.95);
end

% Plotting the data
plot_data(byte_sizes, average_durations, conf_intervals);

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

function plot_data(x, y, yci)
    % Plotting the data with confidence intervals
    figure; hold on;
    
    % Set width for confidence interval cap
    capWidth = 0.01;

    % Plotting the data
    plot(x, y, 'ko', 'MarkerSize', 4, 'LineWidth', 2);
    
    % Draw custom confidence interval
    for i = 1:length(x)
        line([x(i), x(i)], [yci(i,1), yci(i,2)], 'Color', 'k', 'LineWidth', 2);
        line([x(i)-capWidth, x(i)+capWidth], [yci(i,1), yci(i,1)], 'Color', 'k', 'LineWidth', 2);
        line([x(i)-capWidth, x(i)+capWidth], [yci(i,2), yci(i,2)], 'Color', 'k', 'LineWidth', 2);
    end

    set(gca, 'XScale', 'log');
    set(gca, 'XTick', x);
    set(gca, 'XTickLabel', strcat('2^', cellstr(num2str(log2(x)'))));

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

    hold off;
end
