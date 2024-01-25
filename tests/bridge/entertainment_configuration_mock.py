"""Holds configuration mock for the test_entertainment_configuration_repository.py"""

ENTERTAINMENT_CONFIGURATION_MOCK = {
    "errors": [],
    "data": [
        {
            "id": "2022ffc4-1b73-4a43-b376-4c45369bf207",
            "type": "entertainment_configuration",
            "id_v1": "/groups/200",
            "name": "TV area",
            "status": "inactive",
            "configuration_type": "screen",
            "metadata": {"name": "TV area"},
            "stream_proxy": {
                "mode": "auto",
                "node": {
                    "rtype": "entertainment",
                    "rid": "3b8dd390-f7da-4a38-8af1-9a69e859ab62",
                },
            },
            "channels": [
                {
                    "channel_id": 0,
                    "position": {"x": -0.01775, "y": 0.29344, "z": 1.0},
                    "members": [
                        {
                            "service": {
                                "rtype": "entertainment",
                                "rid": "a125e256-43a1-4a54-ac2a-e52d1f9994a9",
                            },
                            "index": 0,
                        }
                    ],
                },
                {
                    "channel_id": 1,
                    "position": {"x": -0.05257, "y": 0.17313, "z": 1.0},
                    "members": [
                        {
                            "service": {
                                "rtype": "entertainment",
                                "rid": "b4f8f77b-8d11-464b-b7cb-2eec6c3f6f4b",
                            },
                            "index": 0,
                        }
                    ],
                },
                {
                    "channel_id": 2,
                    "position": {"x": -0.97048, "y": -0.41407, "z": -0.38769},
                    "members": [
                        {
                            "service": {
                                "rtype": "entertainment",
                                "rid": "0b94aedd-c0d7-40ca-9840-c0a32e2a5180",
                            },
                            "index": 0,
                        }
                    ],
                },
                {
                    "channel_id": 3,
                    "position": {"x": 0.8, "y": -0.8, "z": 0.0},
                    "members": [
                        {
                            "service": {
                                "rtype": "entertainment",
                                "rid": "4983143b-90db-4212-b336-d28aaba824bf",
                            },
                            "index": 0,
                        }
                    ],
                },
                {
                    "channel_id": 4,
                    "position": {"x": 0.0, "y": -0.8, "z": 0.0},
                    "members": [
                        {
                            "service": {
                                "rtype": "entertainment",
                                "rid": "4983143b-90db-4212-b336-d28aaba824bf",
                            },
                            "index": 1,
                        }
                    ],
                },
                {
                    "channel_id": 5,
                    "position": {"x": -0.8, "y": -0.8, "z": 0.0},
                    "members": [
                        {
                            "service": {
                                "rtype": "entertainment",
                                "rid": "4983143b-90db-4212-b336-d28aaba824bf",
                            },
                            "index": 2,
                        }
                    ],
                },
            ],
            "locations": {
                "service_locations": [
                    {
                        "service": {
                            "rtype": "entertainment",
                            "rid": "a125e256-43a1-4a54-ac2a-e52d1f9994a9",
                        },
                        "positions": [{"x": -0.01775, "y": 0.29344, "z": 1.0}],
                        "equalization_factor": 1.0,
                        "position": {"x": -0.01775, "y": 0.29344, "z": 1.0},
                    },
                    {
                        "service": {
                            "rtype": "entertainment",
                            "rid": "b4f8f77b-8d11-464b-b7cb-2eec6c3f6f4b",
                        },
                        "positions": [{"x": -0.05257, "y": 0.17313, "z": 1.0}],
                        "equalization_factor": 1.0,
                        "position": {"x": -0.05257, "y": 0.17313, "z": 1.0},
                    },
                    {
                        "service": {
                            "rtype": "entertainment",
                            "rid": "0b94aedd-c0d7-40ca-9840-c0a32e2a5180",
                        },
                        "positions": [{"x": -0.97048, "y": -0.41407, "z": -0.38769}],
                        "equalization_factor": 1.0,
                        "position": {"x": -0.97048, "y": -0.41407, "z": -0.38769},
                    },
                    {
                        "service": {
                            "rtype": "entertainment",
                            "rid": "4983143b-90db-4212-b336-d28aaba824bf",
                        },
                        "positions": [
                            {"x": 0.57384, "y": -0.59627, "z": -0.83257},
                            {"x": -0.77947, "y": -0.59627, "z": -0.83257},
                        ],
                        "equalization_factor": 1.0,
                        "position": {"x": 0.57384, "y": -0.59627, "z": -0.83257},
                    },
                ]
            },
            "light_services": [
                {"rtype": "light", "rid": "b6f8a28b-cc70-4917-8dbd-25deb8a2b40f"},
                {"rtype": "light", "rid": "48f33cf9-c8e0-41da-90e6-a8f163ff2a18"},
                {"rtype": "light", "rid": "134bef36-714a-4321-a252-b473d44e4b1d"},
                {"rtype": "light", "rid": "85ceab35-b1cb-49ae-ad8c-6e330b14b07a"},
            ],
        }
    ],
}
