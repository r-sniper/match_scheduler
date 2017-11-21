/**
 * Created by onkar on 2/7/17.
 */
var config = {
        container: "#basic-example",

        connectors: {
            type: 'step'
        },
        node: {
            HTMLclass: 'nodeExample1'
        }
    },
    winner= {
        text: {
            name: "winnner",

        },

    },

    f1 = {
        parent: winner,
        text:{
            name: "semis winner1",

        },


    },
    f2 = {
        parent: winner,

        text:{
            name: "semis winner2",

        },

    },
s1 = {
        parent: f1,

        text:{
            name: "s1",

        },

    },
s2 = {
        parent: f1,

        text:{
            name: "s2",

        },

    }
s3= {
        parent: f2,

        text:{
            name: "s3",
        },

    }
s4 = {
        parent: f2,

        text:{
            name: "s4",
        },

    }

    chart_config = [
        config,
        winner,
        f1,
        f2,
		s1,
		s2,
		s3,
		s4
    ];



