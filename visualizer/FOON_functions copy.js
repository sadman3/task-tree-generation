
function init(I) {

	var totalNodes = 0; // -- total number of nodes that are in the network
	interface = I;
	var svg;

	if (file_flag == 0) {
		// -- reading a .TXT file; just split it.
		FOON_graph = FOON_graph.split("\n");
	} else if (file_flag == 1) {
		// -- use JSON reading functions to parse this file:
		FOON_graph = JSON.parse(FOON_graph);
	}

	console.log(FOON_graph);

	var nodes_lvl1 = []; var nodes_lvl2 = []; var nodes_lvl3 = [];
	var FOON_lvl1 = []; var FOON_lvl2 = []; var FOON_lvl3 = [];

	function _checkIfNodeExists(O, H) {
		var objectExisting = -1;
		if (H == 1) {
			for (var N in nodes_lvl1) {
				if (N instanceof ObjectNode && N.equals_functions[H - 1](O)) {
					objectExisting = nodes_lvl1.index(N);
					break;
				}
			}
		} else if (H == 2) {
			for (var N in nodes_lvl2) {
				if (N instanceof ObjectNode && N.equals_functions[H - 1](O)) {
					objectExisting = nodes_lvl2.index(N);
					break;
				}
			}
		} else if (H == 2) {
			for (var N in nodes_lvl3) {
				if (N instanceof ObjectNode && N.equals_functions[H - 1](O)) {
					objectExisting = nodes_lvl3.index(N);
					break;
				}
			}
		}
		return objectExisting;
	}

	function _checkIfFUExists(U, A) {
		if (A == 1) {
			if (FOON_lvl1.length == 0) {
				return false;
			}
			for (var F = 0; F < FOON_lvl1.length; F++) {
				if (FOON_lvl1[F].equals_lvl1(U)) {
					return true;
				}
			}
			return false;
		}
		if (A == 2) {
			if (FOON_lvl2.length == 0) {
				return false;
			}
			for (var F = 0; F < FOON_lvl2.length; F++) {
				if (FOON_lvl2[F].equals_lvl2(U)) {
					return true;
				}
			}
			return false;
		}
		if (A == 3) {
			if (FOON_lvl3.length == 0) {
				return false;
			}
			for (var F = 0; F < FOON_lvl3.length; F++) {
				if (FOON_lvl3[F].equals_lvl3(U)) {
					// console.log("duplicate:");
					// console.log(FOON_lvl3[F]);
					// console.log(U);
					return true;
				}
			}
			return false;
		}
	}

	function _addObjectToFOON(newObject, isInput, D, newFU_lvl3, newFU_lvl2, newFU_lvl1) {
		// -- check if object already exists within the list so as to avoid duplicates
		var objectExisting = _checkIfNodeExists(newObject, 3);
		if (objectExisting == -1) {
			// -- just add new object to the list of all nodes
			nodes_lvl3.push(newObject);
			objectIndex = totalNodes;
			totalNodes += 1;
		} else {
			objectIndex = objectExisting;
		}

		if (isInput == true) {
			// -- this Object will be an input node to the FU:
			newFU_lvl3.addObjectNode(nodes_lvl3[objectIndex], 1, (D));
		} else {
			// -- add the Objects as output nodes to the FU:
			newFU_lvl3.addObjectNode(nodes_lvl3[objectIndex], 2, (D));
			// -- make the connection from Motion to Object
			// newFU_lvl3.getMotionNode().addNeighbour(nodes_lvl3[objectIndex]);
		}

		// NOTE: Creating level 2 version of this node:
		newObject_lvl2 = new ObjectNode(newObject.getObjectType(), newObject.getObjectLabel());

		for (var J = 0; J < newObject.getStatesList().length; J++) {
			newObject_lvl2.addStateType([(newObject.getStatesList()[J][0]), newObject.getStatesList()[J][1], newObject.getStatesList()[J][2]]);
		}

		objectExisting = _checkIfNodeExists(newObject_lvl2, 2);

		// -- check if object already exists within the list so as to avoid duplicates
		if (objectExisting == -1) {
			// -- just add new object to the list of all nodes
			objectIndex = nodes_lvl2.length;
			nodes_lvl2.push(newObject_lvl2);
		} else {
			objectIndex = objectExisting;
		}

		if (isInput == true) {
			newFU_lvl2.addObjectNode(nodes_lvl2[objectIndex], 1, (D));
		} else {
			newFU_lvl2.addObjectNode(nodes_lvl2[objectIndex], 2, (D));
			// newFU_lvl2.getMotionNode().addNeighbour(nodes_lvl2[objectIndex]);
		}

		// NOTE: Creating level 1 version of this node:
		newObject_lvl1 = new ObjectNode(newObject.getObjectType(), newObject.getObjectLabel());

		objectExisting = _checkIfNodeExists(newObject_lvl1, 1);

		// -- check if object already exists within the list so as to avoid duplicates
		if (objectExisting == -1) {
			objectIndex = nodes_lvl1.length;
			nodes_lvl1.push(newObject_lvl1);
		} else {
			objectIndex = objectExisting;
		}

		if (isInput == true) {
			newFU_lvl1.addObjectNode(nodes_lvl1[objectIndex], 1, (D));
		} else {
			newFU_lvl1.addObjectNode(nodes_lvl1[objectIndex], 2, (D));
			// newFU_lvl1.getMotionNode().addNeighbour(nodes_lvl1[objectIndex]);
		}
	}

	function constructFOON_old() {
		// -- 'totalNodes' - the number of object AND motion nodes are in FOON.
		var count = totalNodes;
		var stateParts, objectParts, motionParts; // objects used to contain the split strings

		var objectIndex = -1; // variables to hold position of object/motion within list of Things
		var isInput = true, newObject = null;
		var newFU_lvl3 = new FunctionalUnit(); var newFU_lvl2 = new FunctionalUnit(); var newFU_lvl1 = new FunctionalUnit(); // object which will hold the functional unit being read.

		for (var I = 0; I < FOON_graph.length; I++) {
			var line = FOON_graph[I];
			console.log(I + " - " + line);

			objectExisting = -1;
			if (line.startsWith("//")) {
				if (newObject != null) {
					objectExisting = -1;
					// -- checking if the Object node exists in the list of objects:
					for (var N = 0; N < nodes_lvl3.length; N++) {
						if (nodes_lvl3[N] instanceof ObjectNode && (nodes_lvl3[N]).equals_lvl3(newObject)) {
							objectExisting = nodes_lvl3.indexOf(nodes_lvl3[N]);
						}
					}

					// Check if object already exists within the list so as to avoid duplicates
					if (objectExisting != -1) {
						objectIndex = objectExisting;
					}
					else {
						// just add new ObjectNode to the list of all nodes
						nodes_lvl3.push(newObject);
						objectIndex = count++;
					}

					if (isInput) {
						// this Object will be an input node to the FU
						newFU_lvl3.addObjectNode(nodes_lvl3[objectIndex], 0, objectParts[2]);
					} else {
						// add the Objects as output nodes to the Functional Unit
						newFU_lvl3.addObjectNode(nodes_lvl3[objectIndex], 1, objectParts[2]);
					}

					// Functional Unit - Level 2:
					objectExisting = -1;
					newObject_lvl2 = new ObjectNode(objectParts[0], objectParts[1]);

					for (var J = 0; J < newObject.getStatesList().length; J++) {
						newObject_lvl2.addStateType([newObject.getStateType(J), newObject.getStateLabel(J), []])
					}

					// checking if Object node exists in the list of objects
					for (var N = 0; N < nodes_lvl2.length; N++) {
						if (nodes_lvl2[N] instanceof ObjectNode && (nodes_lvl2[N]).equals_lvl2(newObject_lvl2)) {
							objectExisting = nodes_lvl2.indexOf(nodes_lvl2[N]);
						}
					}

					// Check if object already exists within the list so as to avoid duplicates
					if (objectExisting != -1) {
						objectIndex = objectExisting;
					}
					else {
						// just add new ObjectNode to the list of all nodes
						objectIndex = nodes_lvl2.length;
						nodes_lvl2.push(newObject_lvl2);
					}

					if (isInput) {
						// this Object will be an input node to the FU
						newFU_lvl2.addObjectNode(nodes_lvl2[objectIndex], 0, objectParts[2]);
					} else {
						// add the Objects as output nodes to the Functional Unit
						newFU_lvl2.addObjectNode(nodes_lvl2[objectIndex], 1, objectParts[2]);
					}

					objectExisting = -1;
					newObject_lvl1 = new ObjectNode(objectParts[0], objectParts[1]);

					// checking if Object node exists in the list of objects
					for (var N = 0; N < nodes_lvl1.length; N++) {
						if (nodes_lvl1[N] instanceof ObjectNode && nodes_lvl1[N].equals_lvl1(newObject_lvl1)) {
							objectExisting = nodes_lvl1.indexOf(nodes_lvl1[N]);
						}
					}

					// Check if object already exists within the list so as to avoid duplicates
					if (objectExisting != -1) {
						objectIndex = objectExisting;
					}
					else {
						// just add new ObjectNode to the list of all nodes
						objectIndex = nodes_lvl1.length;
						nodes_lvl1.push(newObject_lvl1);
					}

					if (isInput) {
						// this Object will be an input node to the FU
						newFU_lvl1.addObjectNode(nodes_lvl1[objectIndex], 0, objectParts[2]);
					} else {
						// add the Objects as output nodes to the Functional Unit
						newFU_lvl1.addObjectNode(nodes_lvl1[objectIndex], 1, objectParts[2]);
					}

				}

				if (!_checkIfFUExists(newFU_lvl1, 1)) {
					nodes_lvl1.push(newFU_lvl1.getMotionNode());	// no matter what, we add new MotionNode nodes; we will have multiple instances everywhere.
					FOON_lvl1.push(newFU_lvl1);
				}
				if (!_checkIfFUExists(newFU_lvl2, 2)) {
					FOON_lvl2.push(newFU_lvl2);
					nodes_lvl2.push(newFU_lvl2.getMotionNode());	// no matter what, we add new MotionNode nodes; we will have multiple instances everywhere.
				}
				if (!_checkIfFUExists(newFU_lvl3, 3)) {
					nodes_lvl3.push(newFU_lvl3.getMotionNode());	// no matter what, we add new MotionNode nodes; we will have multiple instances everywhere.
					FOON_lvl3.push(newFU_lvl3);
					count++; // increment number of nodes by one since we are adding a new MotionNode node
				}

				// -- we are adding a new FU, so start from scratch..
				newFU_lvl3 = new FunctionalUnit(); newFU_lvl2 = new FunctionalUnit(); newFU_lvl1 = new FunctionalUnit(); // create an entirely new FU object to proceed with reading new units.
				isInput = true; newObject = null; // this is the end of a FU so we will now be adding input nodes; set flag to TRUE.
			} else if (line.startsWith("O")) {
				if (newObject != null) {
					var objectExisting = -1;
					// -- checking if the Object node exists in the list of objects:
					for (var N = 0; N < nodes_lvl3.length; N++) {
						if (nodes_lvl3[N] instanceof ObjectNode && (nodes_lvl3[N]).equals_lvl3(newObject)) {
							objectExisting = nodes_lvl3.indexOf(nodes_lvl3[N]);
						}
					}

					// Check if object already exists within the list so as to avoid duplicates
					if (objectExisting != -1) {
						objectIndex = objectExisting;
					}
					else {
						// just add new ObjectNode to the list of all nodes
						nodes_lvl3.push(newObject);
						objectIndex = count++;
					}

					if (isInput) {
						// this Object will be an input node to the FU
						newFU_lvl3.addObjectNode(nodes_lvl3[objectIndex], 0, objectParts[2]);
					} else {
						// add the Objects as output nodes to the Functional Unit
						newFU_lvl3.addObjectNode(nodes_lvl3[objectIndex], 1, objectParts[2]);
					}

					// Functional Unit - Level 2:
					objectExisting = -1;
					newObject_lvl2 = new ObjectNode(objectParts[0], objectParts[1]);

					for (var J = 0; J < newObject.getStatesList().length; J++) {
						newObject_lvl2.addStateType([newObject.getStateType(J), newObject.getStateLabel(J), []])
					}

					// checking if Object node exists in the list of objects
					for (var N = 0; N < nodes_lvl2.length; N++) {
						if (nodes_lvl2[N] instanceof ObjectNode && (nodes_lvl2[N]).equals_lvl2(newObject_lvl2)) {
							objectExisting = nodes_lvl2.indexOf(nodes_lvl2[N]);
						}
					}

					// Check if object already exists within the list so as to avoid duplicates
					if (objectExisting != -1) {
						objectIndex = objectExisting;
					}
					else {
						// just add new ObjectNode to the list of all nodes
						objectIndex = nodes_lvl2.length;
						nodes_lvl2.push(newObject_lvl2);
					}

					if (isInput) {
						// this Object will be an input node to the FU
						newFU_lvl2.addObjectNode(nodes_lvl2[objectIndex], 0, objectParts[2]);
					} else {
						// add the Objects as output nodes to the Functional Unit
						newFU_lvl2.addObjectNode(nodes_lvl2[objectIndex], 1, objectParts[2]);
					}

					objectExisting = -1;
					newObject_lvl1 = new ObjectNode(objectParts[0], objectParts[1]);

					// checking if Object node exists in the list of objects
					for (var N = 0; N < nodes_lvl1.length; N++) {
						if (nodes_lvl1[N] instanceof ObjectNode && nodes_lvl1[N].equals_lvl1(newObject_lvl1)) {
							objectExisting = nodes_lvl1.indexOf(nodes_lvl1[N]);
						}
					}

					// Check if object already exists within the list so as to avoid duplicates
					if (objectExisting != -1) {
						objectIndex = objectExisting;
					}
					else {
						// just add new ObjectNode to the list of all nodes
						objectIndex = nodes_lvl1.length;
						nodes_lvl1.push(newObject_lvl1);
					}

					if (isInput) {
						// this Object will be an input node to the FU
						newFU_lvl1.addObjectNode(nodes_lvl1[objectIndex], 0, objectParts[2]);
					} else {
						// add the Objects as output nodes to the Functional Unit
						newFU_lvl1.addObjectNode(nodes_lvl1[objectIndex], 1, objectParts[2]);
					}

				}

				// -- this is an Object node, so we probably should read the next line one time
				objectParts = line.split("O", 2); // get the Object identifier by splitting first instance of O
				objectParts = objectParts[1].split("\t");

				newObject = new ObjectNode(objectParts[0], objectParts[1]);

			} else if (line.startsWith("S")) {

				// -- get the Object's state identifier by splitting first instance of S
				stateParts = line.split("S", 2);
				stateParts = stateParts[1].split("\t").filter(Boolean);
				console.log(stateParts);

				var list_ingredients = [];
				// -- check if this object is a container:
				if (stateParts.length > 2 && stateParts[2].startsWith("{")) {
					var ingredients = stateParts[2];
					ingredients = ingredients.split("{");
					ingredients = ingredients[1].split("}");
					ingredients = ingredients.filter(Boolean);
					console.log(ingredients);
					// -- we then need to make sure that there are ingredients to be read!
					if (ingredients.length > 0) {
						ingredients = ingredients[0].split(",");
						for (var J = 0; J < ingredients.length; J++) {
							list_ingredients.push(ingredients[J]);
						}
						list_ingredients.sort();
					}
				}

				newObject.addStateType([stateParts[0], stateParts[1], list_ingredients]);

			} else if (line.startsWith("M")) {
				if (newObject != null) {
					var objectExisting = -1;
					// -- checking if the Object node exists in the list of objects:
					for (var N = 0; N < nodes_lvl3.length; N++) {
						if (nodes_lvl3[N] instanceof ObjectNode && (nodes_lvl3[N]).equals_lvl3(newObject)) {
							objectExisting = nodes_lvl3.indexOf(nodes_lvl3[N]);
						}
					}

					// Check if object already exists within the list so as to avoid duplicates
					if (objectExisting != -1) {
						objectIndex = objectExisting;
					}
					else {
						// just add new ObjectNode to the list of all nodes
						nodes_lvl3.push(newObject);
						objectIndex = count++;
					}

					if (isInput) {
						// this Object will be an input node to the FU
						newFU_lvl3.addObjectNode(nodes_lvl3[objectIndex], 0, objectParts[2]);
					} else {
						// add the Objects as output nodes to the Functional Unit
						newFU_lvl3.addObjectNode(nodes_lvl3[objectIndex], 1, objectParts[2]);
					}

					// Functional Unit - Level 2:
					objectExisting = -1;
					newObject_lvl2 = new ObjectNode(objectParts[0], objectParts[1]);

					for (var J = 0; J < newObject.getStatesList().length; J++) {
						newObject_lvl2.addStateType([newObject.getStateType(J), newObject.getStateLabel(J), []])
					}

					// checking if Object node exists in the list of objects
					for (var N = 0; N < nodes_lvl2.length; N++) {
						if (nodes_lvl2[N] instanceof ObjectNode && (nodes_lvl2[N]).equals_lvl2(newObject_lvl2)) {
							objectExisting = nodes_lvl2.indexOf(nodes_lvl2[N]);
						}
					}

					// Check if object already exists within the list so as to avoid duplicates
					if (objectExisting != -1) {
						objectIndex = objectExisting;
					}
					else {
						// just add new ObjectNode to the list of all nodes
						objectIndex = nodes_lvl2.length;
						nodes_lvl2.push(newObject_lvl2);
					}

					if (isInput) {
						// this Object will be an input node to the FU
						newFU_lvl2.addObjectNode(nodes_lvl2[objectIndex], 0, objectParts[2]);
					} else {
						// add the Objects as output nodes to the Functional Unit
						newFU_lvl2.addObjectNode(nodes_lvl2[objectIndex], 1, objectParts[2]);
					}

					objectExisting = -1;
					newObject_lvl1 = new ObjectNode(objectParts[0], objectParts[1]);

					// checking if Object node exists in the list of objects
					for (var N = 0; N < nodes_lvl1.length; N++) {
						if (nodes_lvl1[N] instanceof ObjectNode && nodes_lvl1[N].equals_lvl1(newObject_lvl1)) {
							objectExisting = nodes_lvl1.indexOf(nodes_lvl1[N]);
						}
					}

					// Check if object already exists within the list so as to avoid duplicates
					if (objectExisting != -1) {
						objectIndex = objectExisting;
					}
					else {
						// just add new ObjectNode to the list of all nodes
						objectIndex = nodes_lvl1.length;
						nodes_lvl1.push(newObject_lvl1);
					}

					if (isInput) {
						// this Object will be an input node to the FU
						newFU_lvl1.addObjectNode(nodes_lvl1[objectIndex], 0, objectParts[2]);
					} else {
						// add the Objects as output nodes to the Functional Unit
						newFU_lvl1.addObjectNode(nodes_lvl1[objectIndex], 1, objectParts[2]);
					}

				}
				newObject = null;
				// We are adding a Motion node, so very easy to deal with
				motionParts = line.split("M", 2); // get the Motion number
				motionParts = motionParts[1].split("\t"); // get the Motion label

				// -- FUNCTIONAL UNITS WITH INGREDIENTS...
				// create new MotionNode based on what was read.
				var newMotion = new MotionNode(motionParts[0], motionParts[1]);
				newFU_lvl3.setMotionNode(newMotion);
				newFU_lvl3.setTimes(motionParts[2], motionParts[3]);
				if (motionParts.length > 4) {
					newFU_lvl3.setIndication(motionParts[4]);
					newFU_lvl3.setSuccessRate(motionParts[5]);
				}

				// -- FUNCTIONAL UNITS WITHOUT INGREDIENTS...
				newMotion = new MotionNode(motionParts[0], motionParts[1]);
				newFU_lvl2.setMotionNode(newMotion);
				newFU_lvl2.setTimes(motionParts[2], motionParts[3]);
				if (motionParts.length > 4) {
					newFU_lvl2.setIndication(motionParts[4]);
					newFU_lvl2.setSuccessRate(motionParts[5]);
				}

				// -- FUNCTIONAL UNITS WITHOUT STATES/INGREDIENTS...
				newMotion = new MotionNode(motionParts[0], motionParts[1]);
				newFU_lvl1.setMotionNode(newMotion);
				newFU_lvl1.setTimes(motionParts[2], motionParts[3]);
				if (motionParts.length > 4) {
					newFU_lvl1.setIndication(motionParts[4]);
					newFU_lvl1.setSuccessRate(motionParts[5]);
				}

				isInput = false;
			}
			else { }
		}
		return count;
	}

	function _constructFOON_as_txt() {
		var isInput = true;
		var stateParts, objectParts, motionParts; // -- objects used to contain the split strings
		var newObject = null;

		// -- objects which will hold the functional unit being read:
		newFU_lvl3 = new FunctionalUnit(); newFU_lvl2 = new FunctionalUnit(); newFU_lvl1 = new FunctionalUnit()

		for (var L = 0; L < FOON_graph.length; L++) {
			var line = FOON_graph[L];
			line = line.replace(/[\s\r\n]+$/, '');
			console.log(L + " : " + line);

			if (line.startsWith("# Source:")) {
				continue;

			} else if (line.startsWith("//")) {
				if (newFU_lvl3.getInputList().length === 0 && newFU_lvl3.getOutputList().length === 0)
					continue;

				if (newObject != null)
					_addObjectToFOON(newObject, isInput, objectParts[2], newFU_lvl3, newFU_lvl2, newFU_lvl1);

				// -- we are adding a new FU, so start from scratch..
				if (_checkIfFUExists(newFU_lvl3, 3) == false) {
					// NOTE: no matter what, we add new motion nodes; we will have multiple instances everywhere.	
					nodes_lvl3.push(newFU_lvl3.getMotionNode());
					FOON_lvl3.push(newFU_lvl3);
					// -- we only keep track of the total number of nodes in the LVL3 FOON.
					totalNodes += 1;
				}
				if (_checkIfFUExists(newFU_lvl2, 2) == false) {
					nodes_lvl2.push(newFU_lvl2.getMotionNode());
					FOON_lvl2.push(newFU_lvl2);
				}
				if (_checkIfFUExists(newFU_lvl1, 1) == false) {
					nodes_lvl1.push(newFU_lvl1.getMotionNode());
					FOON_lvl1.push(newFU_lvl1);
				}

				// -- create an entirely new FU object to proceed with reading new units.			
				newFU_lvl3 = new FunctionalUnit(); newFU_lvl2 = new FunctionalUnit(); newFU_lvl1 = new FunctionalUnit()

				// -- this is the end of a FU so we will now be adding input nodes; set flag to TRUE.
				isInput = true; newObject = null;
			} else if (line.startsWith("O")) {
				// -- we have an Object already in consideration which we were pushing states to:
				if (newObject != null)
					_addObjectToFOON(newObject, isInput, objectParts[2], newFU_lvl3, newFU_lvl2, newFU_lvl1);
				// -- this is an Object node, so we probably should read the next line one time
				// -- get the Object identifier by splitting first instance of O
				objectParts = line.split("O"); objectParts = objectParts[1].split("\t");
				newObject = new ObjectNode((objectParts[0]), objectParts[1]);
			} else if (line.startsWith("S")) {
				// -- get the Object's state identifier by splitting first instance of S
				stateParts = line.split("S");
				stateParts = stateParts[1].split("\t").filter(Boolean);

				// -- check if this object is a container:
				var list_ingredients = []; var relative_object = null;
				if (stateParts.length > 2) {
					if (stateParts[2].startsWith("{")) {
						var ingredients = stateParts[2];
						ingredients = ingredients.split("{");
						ingredients = ingredients[1].split("}").filter(Boolean);

						// -- we then need to make sure that there are ingredients to be read.
						if (ingredients.length > 0) {
							ingredients = ingredients[0].split(",");
							// console.log(ingredients);
							for (var I in ingredients) {
								list_ingredients.push(ingredients[I]);
							}
							list_ingredients.sort();
						}
					} else if (stateParts[2].startsWith("[")) {
						var relater = stateParts[2];
						relater = relater.split("[");
						relater = relater[1].split("]").filter(Boolean);
						relative_object = relater[0];
					}

				}

				console.log(list_ingredients);
				newObject.addStateType([(stateParts[0]), stateParts[1], relative_object]);
				if (list_ingredients.length > 0)
					newObject.setIngredients(list_ingredients);
			} else if (line.startsWith("L")) {
				// -- get the Object's location by splitting first instance of L:
				locationParts = line.split("L");
				locationParts = locationParts[1].split("\t").filter(Boolean);
				newObject.setObjectLocation([locationParts[0], locationParts[1]]);
			} else if (line.startsWith("M")) {
				if (newObject != null) {
					_addObjectToFOON(newObject, isInput, objectParts[2], newFU_lvl3, newFU_lvl2, newFU_lvl1);
				}
				newObject = null;

				// -- We are adding a Motion node, so very easy to deal with, as follows:
				motionParts = line.split("M");		// -- get the Motion number...
				motionParts = motionParts[1].split("\t"); //	... and get the Motion label

				// Functional Unit - Level 3:
				// -- create new Motion based on what was read:
				newMotion = new MotionNode((motionParts[0]), motionParts[1]);
				// for (var T in newFU_lvl3.getInputList())
				// 	T.addNeighbour(newMotion); // -- make the connection from Object(s) to Motion
				newFU_lvl3.setMotionNode(newMotion);
				newFU_lvl3.setTimes(motionParts[2], motionParts[3]);

				// -- this is to check for the new version of FOON with robot/human difficulties:
				if (motionParts.length > 4) {
					// -- this will indicate whether motion is done by robot or human
					newFU_lvl3.setIndication(motionParts[4]);
					newFU_lvl3.setSuccessRate((motionParts[5]));
				}

				// Functional Unit - Level 2:
				newMotion = new MotionNode((motionParts[0]), motionParts[1]);
				// for (var T in newFU_lvl2.getInputList())
				// 	T.addNeighbour(newMotion);
				newFU_lvl2.setMotionNode(newMotion);
				newFU_lvl2.setTimes(motionParts[2], motionParts[3]);

				// -- this is to check for the new version of FOON with robot/human difficulties:
				if (motionParts.length > 4) {
					// -- this will indicate whether motion is done by robot or human:
					// -- the success rate is given by a decimal number between 0 and 1 (inclusive).
					newFU_lvl2.setIndication(motionParts[4]);
					console.log(parseFloat(motionParts[5]));
					console.log(motionParts[5]);
					newFU_lvl2.setSuccessRate(parseFloat(motionParts[5]));
				}

				// Functional Unit - Level 1:
				newMotion = new MotionNode((motionParts[0]), motionParts[1]);
				// for (var T in newFU_lvl1.getInputList())
				// 	T.addNeighbour(newMotion);
				newFU_lvl1.setMotionNode(newMotion);
				newFU_lvl1.setTimes(motionParts[2], motionParts[3]);

				// -- this is to check for the new version of FOON with robot/human difficulties:
				if (motionParts.length > 4) {
					// -- this will indicate whether motion is done by robot or human
					// -- the success rate is given by a decimal number between 0 and 1 (inclusive).
					newFU_lvl1.setIndication(motionParts[4]);
					newFU_lvl1.setSuccessRate((motionParts[5]));
				}

				isInput = false;	// -- we will now switch over to adding output nodes since we have seen a motion node
			} else { }
		}
		return;
	}

	function _constructFOON_as_JSON() {
		var newFU_lvl3 = new FunctionalUnit(), newFU_lvl2 = new FunctionalUnit(), newFU_lvl1 = new FunctionalUnit();
		var _json = FOON_graph;

		for (var func_unit of _json['functional_units']) {

			console.log(func_unit);

			for (var _input of func_unit['input_nodes']) {
				// -- level 3 version:
				var newObject = new ObjectNode((_input['object_id']), _input['object_label']);

				for (var S of _input['object_states'])
					if ('relative_object' in S)
						newObject.addStateType([(S['state_id']), S['state_label'], S['relative_object']]);
					else
						newObject.addStateType([(S['state_id']), S['state_label'], null]);

				for (var I of _input['ingredients'])
					// -- if not, just stick to object-label-only ingredients as done before
					newObject.addIngredient(I);

				if ('object_location' in _input)
					newObject.setObjectLocation(_input['object_location']);

				_addObjectToFOON(newObject, true, _input['object_in_motion'], newFU_lvl3, newFU_lvl2, newFU_lvl1);
			}

			//	NOTE: reading motion node information:
			// -- level 1 version:
			var newMotion = new MotionNode((func_unit['motion_node']['motion_id']), func_unit['motion_node']['motion_label']);
			newFU_lvl3.setMotionNode(newMotion);
			newFU_lvl3.setTimes(func_unit['motion_node']['start_time'], func_unit['motion_node']['end_time']);

			// for (var T in newFU_lvl3.getInputList())
			// 	T.addNeighbour(newMotion); // -- make the connection from Object(s) to Motion

			// -- this is to check for the new ver;ion of FOON with robot/human difficulties:
			if ('weight_success' in func_unit['motion_node'] == true) {
				// -- this will indicate whether motion is done by robot or human
				newFU_lvl3.setIndication(func_unit['motion_node']['robot_type']);
				newFU_lvl3.setSuccessRate((func_unit['motion_node']['weight_success']));
			}

			// -- level 2 version:
			newMotion = new MotionNode((func_unit['motion_node']['motion_id']), func_unit['motion_node']['motion_label']);
			newFU_lvl2.setMotionNode(newMotion);
			newFU_lvl2.setTimes(func_unit['motion_node']['start_time'], func_unit['motion_node']['end_time']);

			// for (var T in newFU_lvl2.getInputList())
			// 	T.addNeighbour(newMotion); // -- make the connection from Object(s) to Motion

			if ('weight_success' in func_unit['motion_node'] == true) {
				// -- this will indicate whether motion is done by robot or human
				newFU_lvl2.setIndication(func_unit['motion_node']['robot_type']);
				newFU_lvl2.setSuccessRate((func_unit['motion_node']['weight_success']));
			}

			// -- level 1 version:
			newMotion = new MotionNode((func_unit['motion_node']['motion_id']), func_unit['motion_node']['motion_label']);
			newFU_lvl1.setMotionNode(newMotion);
			newFU_lvl1.setTimes(func_unit['motion_node']['start_time'], func_unit['motion_node']['end_time']);

			// for (var T in newFU_lvl1.getInputList())
			// 	T.addNeighbour(newMotion); // -- make the connection from Object(s) to Motion

			if ('weight_success' in func_unit['motion_node']) {
				// -- this will indicate whether motion is done by robot or human
				newFU_lvl1.setIndication(func_unit['motion_node']['robot_type']);
				newFU_lvl1.setSuccessRate((func_unit['motion_node']['weight_success']));
			}


			for (var _output of func_unit['output_nodes']) {
				// -- level 3 version:
				var newObject = new ObjectNode((_output['object_id']), _output['object_label']);

				for (var S of _output['object_states'])
					if ('relative_object' in S)
						newObject.addStateType([(S['state_id']), S['state_label'], S['relative_object']]);
					else
						newObject.addStateType([(S['state_id']), S['state_label'], null]);

				for (var I of _output['ingredients'])
					// -- if not, just stick to object-label-only ingredients as done before
					newObject.addIngredient(I);

				if ('object_location' in _output)
					newObject.setObjectLocation(_output['object_location']);

				_addObjectToFOON(newObject, false, _output['object_in_motion'], newFU_lvl3, newFU_lvl2, newFU_lvl1);
			}

			// NOTE: check if the functional units exist in FOON (exactly as we have seen!)
			if (_checkIfFUExists(newFU_lvl3, 3) == false) {
				// NOTE: no matter what, we add new motion nodes; we will have multiple instances everywhere.	
				nodes_lvl3.push(newFU_lvl3.getMotionNode());
				FOON_lvl3.push(newFU_lvl3);
				// NOTE: we only keep track of the total number of nodes in the LVL3 FOON.
				totalNodes++;
			}

			if (_checkIfFUExists(newFU_lvl2, 2) == false) {
				nodes_lvl2.push(newFU_lvl2.getMotionNode());
				FOON_lvl2.push(newFU_lvl2);
			}

			if (_checkIfFUExists(newFU_lvl1, 1) == false) {
				nodes_lvl1.push(newFU_lvl1.getMotionNode());
				FOON_lvl1.push(newFU_lvl1);
			}

			// -- create an entirely new FU object to proceed with reading new units.			
			newFU_lvl3 = new FunctionalUnit(); newFU_lvl2 = new FunctionalUnit(); newFU_lvl1 = new FunctionalUnit();
		}
		return;
	}

	function _constructFOON() {
		console.log(file_flag);
		if (file_flag == 0 || file_flag == 2)
			_constructFOON_as_txt();
		else _constructFOON_as_JSON();
	}

	_constructFOON();

	var json = null;
	console.log(level);
	if (level === undefined) {
		response = prompt("What level to visualize? [1/2/3]", "3");
	} else {
		response = level.toString();
	}
	if (response == '2') {
		console.log("FOON Graph constructed!\nLevel 2 Graph contains " + FOON_lvl2.length + " units!");
		json = FOONtoJSON(FOON_lvl2);
	}
	else if (response == '1') {
		console.log("FOON Graph constructed!\nLevel 1 Graph contains " + FOON_lvl1.length + " units!");
		json = FOONtoJSON(FOON_lvl1);
	}
	else {
		console.log("FOON Graph constructed!\nLevel 3 Graph contains " + FOON_lvl3.length + " units!");
		json = FOONtoJSON(FOON_lvl3);
	}
	drawD3Graph(json);
	return json;
}

var interface;

function FOONtoJSON(FOON) {
	// -- reference: http://stackoverflow.com/questions/36856232/write-add-data-in-json-file-using-node-js
	var obj = {
		nodes: [],
		links: []
	};

	count = 0;
	for (FU = 0; FU < FOON.length; FU++) {
		
		// -- adding the nodes section of the JSON file..
		tempList = FOON[FU].getInputList();
		for (U = 0; U < tempList.length; U++) {

			var objectName = tempList[U].getObjectLabel();
			for (var x = 0; x < tempList[U].getStatesList().length; x++) {
				if (!objectName.includes("@states:")){
					if (tempList[U].getStatesList().length > 1) objectName += "@states:"; else objectName += "@state:";
				}
				if (tempList[U].getStateLabel(x).includes("contains"))
					continue;
				objectName += "@	<" + tempList[U].getStateLabel(x).replace(/[\s\r\n]+$/, '')
					+ (tempList[U].getStateRelater(x) != null ? (' [' + tempList[U].getStateRelater(x) + ']') : "") + ">";
			}
			if (tempList[U].getIngredients().length > 0)
				objectName += "@	<contains: " + String(tempList[U].getIngredients()) + ">";

			found = false;
			for (V = 0; V < obj.nodes.length; V++) {
				if (obj.nodes[V].id === objectName) {
					found = true;
				}
			}
			if (found == false) {
				obj.nodes.push({ id: objectName, type: 1 });
			}
		}
		tempList = FOON[FU].getOutputList();
		for (U = 0; U < tempList.length; U++) {
			var objectName = tempList[U].getObjectLabel();
			for (var x = 0; x < tempList[U].getStatesList().length; x++) {
				if (!objectName.includes("@states:")){
					if (tempList[U].getStatesList().length > 1) objectName += "@states:"; else objectName += "@state:";
				}
				if (tempList[U].getStateLabel(x).includes("contains"))
					continue;
				objectName += "@	<" + tempList[U].getStateLabel(x).replace(/[\s\r\n]+$/, '')
					+ (tempList[U].getStateRelater(x) != null ? (' [' + tempList[U].getStateRelater(x) + ']') : "") + ">";
			}
			if (tempList[U].getIngredients().length > 0)
				objectName += "@	<contains: " + String(tempList[U].getIngredients()) + ">";

			found = false;
			for (V = 0; V < obj.nodes.length; V++) {
				if (obj.nodes[V].id === objectName) {
					found = true;
				}
			}
			if (found == false) {
				obj.nodes.push({ id: objectName, type: 1 });
			}
		}
		var motionName = (count) + ") " + FOON[FU].getMotionNode().getLabel();
		console.log(FOON[FU].getSuccessRate());
		if (FOON[FU].getSuccessRate() > -1.0)
			motionName += " (SR: " + String(FOON[FU].getSuccessRate()).replace(/[\s\r\n]+$/, '') + ")";
		// console.log(motionName);
		if (motionName.includes("*"))
			// -- this means that it is an "amalgamation" functional unit:
			obj.nodes.push({ id: motionName, type: 4 });
		else {
			if (FOON[FU].getIndication() == "Human") obj.nodes.push({ id: motionName, type: 3 });
			else obj.nodes.push({ id: motionName, type: 2 });
		}

		tempList = FOON[FU].getInputList();
		for (U = 0; U < tempList.length; U++) {
			var src = tempList[U].getObjectLabel();
			for (var x = 0; x < tempList[U].getStatesList().length; x++) {
				if (!src.includes("@states:")){
					if (tempList[U].getStatesList().length > 1) src += "@states:"; else src += "@state:";
				}
				if (tempList[U].getStateLabel(x).includes("contains"))
					continue;
				src += "@	<" + tempList[U].getStateLabel(x).replace(/[\s\r\n]+$/, '')
					+ (tempList[U].getStateRelater(x) != null ? (' [' + tempList[U].getStateRelater(x) + ']') : "") + ">";
			}
			if (tempList[U].getIngredients().length > 0)
				src += "@	<contains: " + String(tempList[U].getIngredients()) + ">";

			var tgt = (count) + ") " + FOON[FU].getMotionNode().getLabel();
			if (FOON[FU].getSuccessRate() > -1.0)
				tgt += " (SR: " + String(FOON[FU].getSuccessRate()).replace(/[\s\r\n]+$/, '') + ")";
			obj.links.push({ source: src, target: tgt });
		}
		tempList = FOON[FU].getOutputList();
		for (U = 0; U < tempList.length; U++) {
			var tgt = tempList[U].getObjectLabel();
			for (var x = 0; x < tempList[U].getStatesList().length; x++) {
				
				if (!tgt.includes("@states:")){
					if (tempList[U].getStatesList().length > 1) tgt += "@states:"; else tgt += "@state:";
				}
				if (tempList[U].getStateLabel(x).includes("contains"))
					continue;
				
				tgt += "@	<" + tempList[U].getStateLabel(x).replace(/[\s\r\n]+$/, '')
					+ (tempList[U].getStateRelater(x) != null ? (' [' + tempList[U].getStateRelater(x) + ']') : "") + ">";
			}
			if (tempList[U].getIngredients().length > 0)
				tgt += "@	<contains: " + String(tempList[U].getIngredients()) + ">";

			var src = (count) + ") " + FOON[FU].getMotionNode().getLabel();
			if (FOON[FU].getSuccessRate() > -1.0)
				src += " (SR: " + String(FOON[FU].getSuccessRate()).replace(/[\s\r\n]+$/, '') + ")";
			obj.links.push({ source: src, target: tgt });
		}
		count++;
	}

	console.log(" -- number of nodes: " + String(obj.nodes.length));
	console.log(" -- number of edges: " + String(obj.links.length));

	if (interface == true) {
		download_JSON(obj)
	}
	console.log("Task tree denoted as:\n" + JSON.stringify(obj));
	return obj;
}

function download_JSON(obj) {
	var download = confirm("Do you want to download the graph file (JSON with source-target format)?");
	if (download == true) {
		var a = document.createElement('a');
		a.setAttribute('href', 'data:text/plain;charset=utf-u,' + encodeURIComponent(JSON.stringify(obj)));
		a.setAttribute('download', String(file_name + '.json'));
		a.click();
	}
}

function download_PDF(){
	// Source: https://stackoverflow.com/questions/61800343/d3-js-version-5-chart-to-pdf
	const svgToPdfExample = (svg) => {
		const doc = new window.PDFDocument({ size: [1200, 1200]});
		const chunks = [];
		const stream = doc.pipe({
			// writable stream implementation
			write: (chunk) => chunks.push(chunk),
			end: () => {
				const pdfBlob = new Blob(chunks, {
					type: "application/octet-stream",
				});
				var blobUrl = URL.createObjectURL(pdfBlob);
				//window.open(`${blobUrl}?customfilename.pdf`);
				
				/* custom file name download */
				const a = document.createElement("a");
				document.body.appendChild(a);
				a.style = "display: none";
				a.href = blobUrl;
				a.download =  String(file_name + '.pdf'); // <---- 👈 file name
				a.click();
				window.URL.revokeObjectURL(url);
			},
			// readable streaaam stub iplementation
			on: (event, action) => {},
			once: (...args) => {},
			emit: (...args) => {},
		});
	
		window.SVGtoPDF(doc, svg, 0, 0, {width: 1200 * 4/3, height: 1200 * 4/3, fontCallback: () => 'Helvetica'});
	
		doc.end();
	};		 
	const svgElement = document.getElementById("svg");
	svgToPdfExample(svgElement.innerHTML);

}

function FOONtoJSON_onemode(FOON) {
	// -- reference: http://stackoverflow.com/questions/36856232/write-add-data-in-json-file-using-node-js
	var obj = {
		nodes: [],
		links: []
	};

	count = 0;
	for (FU = 0; FU < FOON.length; FU++) {
		// console.log(FOON[FU]);
		// -- adding the nodes section of the JSON file..
		tempList = FOON[FU].getInputList();
		for (U = 0; U < tempList.length; U++) {
			// console.log(tempList[U]);
			var objectName = tempList[U].getObjectLabel();
			if (tempList[U].getIngredients().length > 0)
				objectName += "@contains: " + String(tempList[U].getIngredients()) + "}";
			for (var x = 0; x < tempList[U].getStatesList().length; x++) {
				if (tempList[U].getStateLabel(x).includes("contains"))
					continue;
				if (!objectName.includes("@states:"))
					objectName += "@states:"
				objectName += "@	<" + tempList[U].getStateLabel(x).replace(/[\s\r\n]+$/, '')
					+ (tempList[U].getStateRelater(x) != null ? (' [' + tempList[U].getStateRelater(x) + ']') : "") + ">";
			}

			found = false;
			for (V = 0; V < obj.nodes.length; V++) {
				if (obj.nodes[V].id === objectName) {
					found = true;
				}
			}
			if (found == false) {
				obj.nodes.push({ id: objectName, type: 1 });
			}
		}
		tempList = FOON[FU].getOutputList();
		for (U = 0; U < tempList.length; U++) {
			var objectName = tempList[U].getObjectLabel();
			if (tempList[U].getIngredients().length > 0)
				objectName += "@contains: " + String(tempList[U].getIngredients()) + "}";
			for (var x = 0; x < tempList[U].getStatesList().length; x++) {
				if (tempList[U].getStateLabel(x).includes("contains"))
					continue;
				if (!objectName.includes("@states:"))
					objectName += "@states:"
				objectName += "@	<" + tempList[U].getStateLabel(x).replace(/[\s\r\n]+$/, '')
					+ (tempList[U].getStateRelater(x) != null ? (' [' + tempList[U].getStateRelater(x) + ']') : "") + ">";
			}

			found = false;
			for (V = 0; V < obj.nodes.length; V++) {
				if (obj.nodes[V].id === objectName) {
					found = true;
				}
			}
			if (found == false) {
				obj.nodes.push({ id: objectName, type: 1 });
			}
		}

		tempList = FOON[FU].getInputList();
		for (F = 0; F < tempList.length; F++) {
			var src = tempList[F].getObjectLabel();
			if (tempList[U].getIngredients().length > 0)
				src += "@contains: " + String(tempList[U].getIngredients()) + "}";
			for (var x = 0; x < tempList[F].getStatesList().length; x++) {
				if (tempList[U].getStateLabel(x).includes("contains"))
					continue;
				if (!src.includes("@states:"))
					src += "@states:"
				src += "@	<" + tempList[U].getStateLabel(x).replace(/[\s\r\n]+$/, '')
					+ (tempList[U].getStateRelater(x) != null ? (' [' + tempList[U].getStateRelater(x) + ']') : "") + ">";
			}

			target_list = FOON[FU].getOutputList();
			for (U = 0; U < target_list.length; U++) {
				var tgt = target_list[U].getObjectLabel();
				if (tempList[U].getIngredients().length > 0)
					tgt += "@contains: " + String(tempList[U].getIngredients()) + "}";
				for (var y = 0; y < target_list[U].getStatesList().length; y++) {
					if (tempList[U].getStateLabel(x).includes("contains"))
						continue;
					if (!tgt.includes("@states:"))
						tgt += "@states:"
					tgt += "@	<" + tempList[U].getStateLabel(x).replace(/[\s\r\n]+$/, '')
						+ (tempList[U].getStateRelater(x) != null ? (' [' + tempList[U].getStateRelater(x) + ']') : "") + ">";
				}
				obj.links.push({ source: src, target: tgt });
			}
		}
		count++;
	}

	console.log(" -- number of nodes: " + String(obj.nodes.length));
	console.log(" -- number of edges: " + String(obj.links.length));

	var a = document.createElement('a');
	a.setAttribute('href', 'data:text/plain;charset=utf-u,' + encodeURIComponent(JSON.stringify(obj)));
	a.setAttribute('download', 'output.json');
	a.click()

	console.log("Task tree denoted as:\n" + JSON.stringify(obj));
	return obj;
}


// First character uppercase
function capitalize(s)
{
	if (s)
    	return s[0].toUpperCase() + s.slice(1);
	return "Null"
}

function drawProgressLine(progress_line, file_name) {
	
	progress_line = JSON.parse(progress_line)

	console.log(progress_line)

	file_name = file_name.replace('.json', '')

	if ("ground_truth" in progress_line[0]["state"])
		comparison = true
	else comparison = false



	var headline = d3
		.select("body")
		.append("h2")
		.text("Progress line of recipe: ")
		.append("tspan")
		.text(file_name)
		.style('color', 'darkgreen')


	if (comparison == true) {
		var ingredient = d3.select("body").selectAll("p")
		.data(progress_line)
		.enter()
		.append("p")
		.attr("y", function(d, i) {
			return 40 + i * 40
		})
		.style("background-color", function(d, i) { return i % 2 ? "#eee" : "#ddd"; })
		.style("border-style", "dashed")
		.append("tspan")
		.text(function(d, i ) { return i+1 + ". " + capitalize(d.ingredient)})
		.style("font-weight", "bold")
		.style("color", "blue")
		
		var label1 = ingredient.append("p")
			.attr("y", function(d, i) {
				return 40 + i * 40 
			})
			.text("Generated recipe")
			.style('color', 'brown')
			.style('text-decoration', 'underline')

		var state = ingredient
			.append("p")
			.attr("y", function(d, i) {
				return 40 + i * 40 
			})
			.each(function(d) {
				var ing = d.state.generated
				for(var i = 0; i < ing.length; i++) {
					d3.select(this)
					.append("tspan")
					.text(function(d) {
						if (d.state.generated[i].physical_state) return d.state.generated[i].physical_state
					})
					.style('color', "black")
					.style("font-weight", "semi-bold")
					.append("tspan")
					.text(function(d) {
						if (d.state.generated[i].location.length > 0) return '(' + d.state.generated[i].location + ')'
					})
					.style('color', "slateblue")
					.append("tspan")
					.text(function(d) {
						if (i < ing.length - 1) return " ---> "
					})
					.style('color', "black")
					.append("tspan")
					.text(function(d) {
						if (i < ing.length - 1) return d.motion.generated[i] 
					})
					.style('color', "red")
					.append("tspan")
					.text(function(d) {
						if (i < ing.length - 1) return " ---> "
					})
					.style('color', 'black')
				}
			})

		var end_product = 
			state
			.append("p")
			.attr("y", function(d, i) {
				return 40 + i * 40 
			})
			.text(function(d) {
				return 'End product: ' + capitalize(d.end_product.generated)
			})
			.style('color', 'black')

		var label2 = end_product.append("p")
			.attr("y", function(d, i) {
				return 40 + i * 40 
			})
			.text("Ground truth")
			.style('color', 'brown')
			.style('text-decoration', 'underline')

		var ground_truth_state = end_product
			.append("p")
			.attr("y", function(d, i) {
				return 40 + i * 40 
			})
			.each(function(d) {
				var ing = d.state.ground_truth
				for(var i = 0; i < ing.length; i++) {
					d3.select(this)
					.append("tspan")
					.text(function(d) {
						if (d.state.ground_truth[i].physical_state) return d.state.ground_truth[i].physical_state
					})
					.style('color', "black")
					.style("font-weight", "semi-bold")
					.append("tspan")
					.text(function(d) {
						if (d.state.ground_truth[i].location.length > 0) return '(' + d.state.ground_truth[i].location + ')'
					})
					.style('color', "slateblue")
					.append("tspan")
					.text(function(d) {
						if (i < ing.length - 1) return " ---> "
					})
					.style('color', "black")
					.append("tspan")
					.text(function(d) {
						if (i < ing.length - 1) return d.motion.ground_truth[i] 
					})
					.style('color', "red")
					.append("tspan")
					.text(function(d) {
						if (i < ing.length - 1) return " ---> "
					})
					.style('color', 'black')
				}
			})

		var ground_truth_end_product = 
			ground_truth_state
			.append("p")
			.attr("y", function(d, i) {
				return 40 + i * 40 
			})
			.text(function(d) {
				return 'End product: ' + capitalize(d.end_product.ground_truth)
			})
			.style('color', 'black')
	}
	
	else {
		var ingredient = d3.select("body").selectAll("p")
		.data(progress_line)
		.enter()
		.append("p")
		.attr("y", function(d, i) {
			return 40 + i * 40
		})
		.style("background-color", function(d, i) { return i % 2 ? "#eee" : "#ddd"; })
		.style("border-style", "dashed")
		// .style("border-color", function(d, i) { return i == 0 ? "red" : "black"; })
		.style("padding-left", "5px")
		.append("tspan")
		.text(function(d, i ) { return  i+1 + ". " + capitalize(d.ingredient)})
		.style("font-weight", "bold")
		.style("color", "blue")
		

		var state = ingredient
			.append("p")
			.attr("y", function(d, i) {
				return 40 + i * 40 
			})
			.style("margin-bottom", "0px")
			.style("margin-top", "6px")
			.each(function(d) {
				var ing = d.state.generated
				for(var i = 0; i < ing.length; i++) {
					d3.select(this)
					.append("tspan")
					.text(function(d) {
						if (d.state.generated[i].physical_state) return d.state.generated[i].physical_state
					})
					.style('color', "black")
					.style("font-weight", "semi-bold")
					.append("tspan")
					.text(function(d) {
						if (d.state.generated[i].location.length > 0) return '(' + d.state.generated[i].location + ')'
					})
					.style('color', "green")
					.append("tspan")
					.text(function(d) {
						if (i < ing.length) return " ---> "
					})
					.style('color', "black")
					.append("tspan")
					.text(function(d) {
						if (i < ing.length) return d.motion.generated[i] 
					})
					.style('color', "red")
					.append("tspan")
					.text(function(d) {
						if (i < ing.length - 1) return " ---> "
					})
					.style('color', 'black')
					
				}
			})

		var end_product = 
			state
			.append("p")
			.style("margin-top", "6px")
			.attr("y", function(d, i) {
				return 40 + i * 40 
			})
			.text(function(d) {
				return 'End product: ' + capitalize(d.end_product.generated)
			})
			.style('color', 'black')
			.style('font-family', 'Italic')
		}
		
	
}


function drawD3Graph(graph, S) {

	if (S != undefined) svg = S;
	else svg = d3.select("svg").attr("align", "center");

	var square_length = 24;

	var width = svg.attr("width");
	var height = svg.attr("height");

	svg = svg.call(d3.zoom()
		.on("zoom", zoomed))
		.append("g");

	svg.append("defs")
		.append("marker")
		.attr("id", "arrow")
		.attr("viewBox", "0 -5 10 10")
		.attr("refX", 25)
		.attr("refY", 0)
		.attr("markerWidth", 8)
		.attr("markerHeight", 8)
		.attr("orient", "auto")
		.append("svg:path")
		.style("fill", "#808080")
		//.style("fill", "#000000")	// for creating universal FOON images
		.attr("d", "M0,-5L10,0L0,5");

	var simulation = d3.forceSimulation()
		.force("link", d3.forceLink().id(function (d) { return d.id; }))
		.force("charge", d3.forceManyBody().strength(-300)) // adjust for comfortable spacing
		.force("center", d3.forceCenter(width / 2, height / 2));

	var link = svg.append("g")
		.attr("class", "links")
		.selectAll("line")
		.data(graph.links)
		.enter().append("line")
		.attr("stroke", "#9D9D9D")	// NOTE: was set to "black"
		//.attr("stroke", "#000000")	// for creating universal FOON images
		.attr("marker-end", "url(#arrow)");
		//.attr("stroke-width", "1.25px");

	d3.selectAll("#arrow path").style("fill","#A9A9A9");	

	// NOTE: we can either treat all nodes as equals (i.e. all circles),
	// 	or we can distinguish objects as circles and motions as rectangles:
	var node = svg.append("g")
		.attr("class", "nodes")
		.selectAll("circle")
		.data(graph.nodes)
		.enter()
		// uncomment this line if you want to use circles only:
		.filter(function (d) { return d.type == 1;})
		.append("circle")
		.attr("r", 12) // for regular graph images
		//.attr("r", 28) // for universal FOON images
		.style("fill", function(d) { if (d.type == 1) return "#99FF55"; else if (d.type == 2) return "#E74C3C";}) // #adff2f
		.call(d3.drag()
			.on("start", dragstarted)
			.on("drag", dragged)
			.on("end", dragended))
		.on("mouseover", fade(.08))
		.on("mouseout", fade(1))
		.on("click", function (d) {	console.log("clicked", d.id); });

	// NOTE: uncomment the rest if you want to use square nodes for motions:		
	const mot_node = svg.append("g")
		.attr("class", "nodes")
		.selectAll("rect")
		.data(graph.nodes)
		.enter()
		.filter(function (d) { return d.type != 1;})
		.append("rect")
		// NOTE: for regular FOON graphs, use the following:
		.attr("rx", 6).attr("ry", 6)
		.attr("width", square_length).attr("height", square_length)
		// NOTE: for universal FOON images (without any text), use the following:
		//.attr("rx", 18).attr("ry", 18) 
		//.attr("width", 48).attr("height", 48)
		.style("fill", function (d) {if (d.type == 2) return "#D40000"; else if (d.type == 3) return "#0066FF"; return "4400AA"}) // "#E74C3C"
		.call(d3.drag()
			.on("start", dragstarted)
			.on("drag", dragged)
			.on("end", dragended))
			.on("mouseover", fade(.08))
			.on("mouseout", fade(1))
			.on("click", function (d) {	console.log("clicked", d.id); });

		var text = svg.append("g")
		.attr("class", "labels")
		.selectAll("g")
		.data(graph.nodes)
		.enter().append("g");
	// ... up to here


	// text.push("text")
	// 	.attr("x", 0)
	// 	.attr("y", 20)
	// 	.style("font-family", "sans-serif")
	// 	.style("font-weight", "bold")
	// 	.style("font-size", "0.8em")
	// 	.text(function(d) { return d.id; });

	var separation = 14;
	var textX = -3;
	text.append("text")
		.attr("dy", "0.6em")
		.each(function (d) {
			var lines = d.id.split('@');
			for (var i = 0; i < lines.length; i++) {
				d3.select(this)
					.append("tspan")
					.attr("dy", function (d) { if (i == 0) return 24; return separation; })
					.attr("x", textX)
					.style("text-decoration", function (d) { if (i == 0 && d.type == "1") return "underline"; return "none" })
					.style("fill", function (d) { if (i == 0 && d.type == "1") return "black"; return "black"; })
					.style("font-style", function (d) { if (lines[i].includes(":") && d.type == "1") return "italic"; return "normal"; })
					.style("font-family", "monospace")
					.style("font-weight", function () { if (i == 0) return "bold"; return "semi-bold"; })
					.style("font-size", function (d) { if (d.type == "1" && (lines[i].includes(":") || lines[i].includes("<"))) return "0.8em"; return "0.9em" }) // -- original!
					//.style("font-size", "0em")
					.text(lines[i]);
			}
		});


	node.append("title")
		.text(function (d) { return d.id; });

	mot_node.append("title")
		.text(function (d) { return d.id; });

		
	simulation
		.nodes(graph.nodes)
		.on("tick", ticked);

	simulation.force("link")
		.links(graph.links);

	var linkedByIndex = {};

	graph.links.forEach(function (d) {
		linkedByIndex[d.source.index + "," + d.target.index] = 1;
	});

	function isConnected(a, b) {
		return linkedByIndex[a.index + "," + b.index] || linkedByIndex[b.index + "," + a.index] || a.index == b.index;
	}

	function ticked() {
		link
			.attr("x1", function (d) { return d.source.x; })
			.attr("y1", function (d) { return d.source.y; })
			.attr("x2", function (d) { return d.target.x; })
			.attr("y2", function (d) { return d.target.y; });

		node
			.attr("cx", function (d) { return d.x; })
			.attr("cy", function (d) { return d.y; });

		mot_node
			.attr("x", function (d) { return d.x - square_length / 2; })
			.attr("y", function (d) { return d.y - square_length / 2; });

		text
			.attr("transform", function (d) { return "translate(" + d.x + "," + d.y + ")"; })
	}


	function dragstarted(d) {
		if (!d3.event.active)
			simulation.alphaTarget(0.01).restart();
		d.fx = d.x;
		d.fy = d.y;
	}

	function dragged(d) {
		d.fx = d3.event.x;
		d.fy = d3.event.y;
	}

	function dragended(d) {
		if (!d3.event.active)
			simulation.alphaTarget(0);
		d.fx = d.x;
		d.fy = d.y;
	}

	function zoomed() {
		svg.attr("transform", "translate(" + d3.event.transform.x + "," + d3.event.transform.y + ")" + " scale(" + d3.event.transform.k + ")");
	}

	function fade(opacity) {
		return function (d) {
			node.style("stroke-opacity", function (o) {
				thisOpacity = isConnected(d, o) ? 1 : opacity;
				this.setAttribute('fill-opacity', thisOpacity);
				return thisOpacity;
			});

			mot_node.style("stroke-opacity", function (o) {
				thisOpacity = isConnected(d, o) ? 1 : opacity;
				this.setAttribute('fill-opacity', thisOpacity);
				return thisOpacity;
			});

			link.style("stroke-opacity", opacity).style("stroke-opacity", function (o) {
				return o.source === d || o.target === d ? 1 : opacity;
			});
		};
	}
}

function clear() {
	d3.selectAll("svg > *").remove();
}

function clearProgressLine() {
	d3.selectAll("p").remove();
	d3.selectAll("h2").remove();
}
