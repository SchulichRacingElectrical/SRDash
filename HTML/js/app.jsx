function TableRow(props){
return (
     <tr>
        <td>{props.measurement_date}</td>
        <td>{props.x}</td>
        <td>{props.y}</td>
    </tr>
);

};

TableRow.propTypes = {
        measurement_date: React.PropTypes.string.isRequired,
        x: React.PropTypes.number.isRequired,
        y: React.PropTypes.number.isRequired,
    };



var LiveChart = React.createClass({
    
    propTypes: {
        chartSubtitle: React.PropTypes.string,
        dataTypeID: React.PropTypes.string.isRequired,
        dataTypeName: React.PropTypes.string.isRequired,
        newDataPoint: React.PropTypes.number.isRequired,
        lastUpdateTime: React.PropTypes.instanceOf(Date).isRequired,
        container: React.PropTypes.string.isRequired,
    },

    getDefaultProps: () => {
        return {
          chartSubtitle: null,  
        };
    },
    
    //invoked immediately before rendering when new props or state are being received.
    componentWillUpdate: function(nextProps){
        this.chart.setTitle(null, {text: this.props.chartSubtitle});
        var series = this.chart.get(this.props.dataTypeID)
        // Keep only 100 data points at most in the series
        var shift = series.data.length > 200;
        series.addPoint([nextProps.lastUpdateTime, nextProps.newDataPoint] , true, shift);
    },
    
   componentDidMount: function(){
        this.chart = new Highcharts.Chart({
            title: {
                text: this.props.dataTypeName,
                style: {
                    color: '#FF5733'
                }
            },
            subtitle: {
                text: this.props.chartSubtitle,
                style: {
                    color: '#FF5733'
                }
            },
            
            
            chart: {
                renderTo: this.props.container,
                defaultSeriesType: 'spline',
                backgroundColor: '#1F2739'
            },
            
            xAxis: {
                type: 'datetime',
            },
           
            series:[
                {
                    id: this.props.dataTypeID,
                    name: this.props.dataTypeName,
                    data: [],
                },
            ],
        });
    },

    // Destroy chart before unmount
    componentWillUnmount: function(){
        this.chart.destroy();
    },
    
    render: function(){
        return(
            <div id={this.props.container}> </div>
        );
    },

});


var Application = React.createClass({
    
    componentDidMount: function() {
        // make the Event source connection
        var source = new EventSource('http://localhost:8081/sub?id=system_stats');
        source.onmessage = this.onSystemStatUpdate;

    },
    
    onSystemStatUpdate: function(message){
          var data = JSON.parse(message.data)
          this.setState({
              measurement_date:data.measurement_date,
              x: data.x,
              y: data.y,
              lastUpdateTime: new Date().getTime(),

          }) ;
    },
    
    getInitialState: function() {
        return ({
            processes: [],
            loadAverage: 0.0,
            memoryUsed: 0.0,
            lastUpdateTime:  new Date().getTime(),
        });
    },

    
    render: function(){
        return (
            <div>
            <div className="yellow"> PY TOP </div>
            <table className="table">
                <thead>
                    <tr>
                        <th>measurement_date</th>
                        <th>X</th>
                        <th>Y</th>
                    </tr>
                </thead>
                <tbody>
                {
                    this.state.processes.map(function(proc){
                        return (
                         <TableRow
                             measurement_date={proc.measurement_date}
                             x={proc.x}
                             y={proc.y}/>
                        );
                    })
                }
                </tbody>
            </table>
            <LiveChart 
                className="liveChart"
                dataTypeID='x'
                dataTypeName='x' 
                newDataPoint={this.state.x}
                lastUpdateTime={this.state.lastUpdateTime}
                container='chartloadaverage' />
            
            <LiveChart 
                className="liveChart"
                dataTypeID='y'
                dataTypeName='y' 
                chartSubtitle={'Y: ' + this.state.y}
                newDataPoint={this.state.y}
                lastUpdateTime={this.state.lastUpdateTime}
                container='chartmemoryusage' />
            
            </div>
            
        );
    },
});



ReactDOM.render(<Application />, document.getElementById('container'));